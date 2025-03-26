import { openai } from '@ai-sdk/openai';
import { Message, streamText } from 'ai';
import { NextResponse } from 'next/server';
import { tool_call_test_flow, get_flow } from '@/lib/ai/tools/tool-call'
import { getFlowForPrompt } from '@/app/modules/flows/api/api.server.flow';
import { flow_testing_prompt } from '@/app/prompts/flow_testing_prompt';
import { createOpenRouter } from '@openrouter/ai-sdk-provider';
import { createClient } from '@supabase/supabase-js';

const openrouter = createOpenRouter({
  apiKey: process.env.OPENROUTER_API_KEY || ''
});

const modelName = 'anthropic/claude-3.7-sonnet';

export async function POST(request: Request) {
  try {
    // Check for service account API key first
    const apiKey = request.headers.get('VEYRAX_API_KEY');
    let userId = null;
    let isServiceAccount = false;

    if (apiKey) {
      console.log('Service account API key detected');
      
      if (!process.env.NEXT_PUBLIC_SUPABASE_URL || !process.env.SUPABASE_SERVICE_KEY) {
        console.error('Missing Supabase environment variables');
        return new Response('Server configuration error', { status: 500 });
      }

      const supabase = createClient(
        process.env.NEXT_PUBLIC_SUPABASE_URL,
        process.env.SUPABASE_SERVICE_KEY
      );

      const { data: apiKeyData, error: apiKeyError } = await supabase
        .from('users_api_keys')
        .select('user_id')
        .eq('api_key', apiKey)
        .single();

      if (apiKeyError || !apiKeyData) {
        console.error('API Key validation error:', apiKeyError);
        return new Response('Invalid API key', { status: 401 });
      }

      userId = apiKeyData.user_id;
      isServiceAccount = true;
    }

    const { messages, chatId, flowId } = await request.json();
    
    if (!messages || messages.length === 0) {
      return NextResponse.json(
        { error: 'No messages provided' },
        { status: 400 }
      );
    }

    let currentFlowId = flowId;

    if (!currentFlowId && chatId && !isServiceAccount) {
      const urlMatch = chatId.match(/flow\/([^\/]+)\/edit/);
      if (urlMatch && urlMatch[1]) {
        currentFlowId = urlMatch[1];
      }
    }
    
    const { data: flow } = await getFlowForPrompt(currentFlowId);

    let flowContextInfo = '';
    if (flow) {
      flowContextInfo = `
      Current flow information:
      - ID: ${flow.id}
      - Name: ${flow.name}
      - Description: ${flow.plain_description || ''}
      
      This is the flow that ${isServiceAccount ? 'the service account' : 'user'} wants to test. Use the ID provided above when calling the tool_call_test_flow tool.
      `;
    }

    console.log('flowContextInfo:', flowContextInfo);

    const SystemMainPrompt = `
      You are a helpful assistant that helps ${isServiceAccount ? 'service accounts' : 'users'} test automated workflows.
      Your task is to understand the flow and test its functionality.

      ${flowContextInfo}

      You are tester. You main goal is first call get flows, and then call test flow with the id that ${isServiceAccount ? 'service account' : 'user'} choose.
      
      ${flow ? `The ${isServiceAccount ? 'service account' : 'user'} already has a flow they want to test. Use the current flow ID for testing.` : 'Get flow first, then tool-call to test this out.'}

      ${flow_testing_prompt}

      If flow is empty, you should ask ${isServiceAccount ? 'service account' : 'user'} to create a flow first.

      It is VERY important to use the same param and methods and args that you have received from the get_flow tool.

      It is VERY important.

      For example, if provider slug is "google-calendar" it means that you should use the google-calendar tool, and methods as action_slug. 
    `;

    console.log('SystemMainPrompt:', SystemMainPrompt);

    const allMessages = [
      { role: 'system', content: SystemMainPrompt, id: 'system' },
      ...messages
    ];

    const response = streamText({
      model: openrouter(modelName) as any,
      messages: allMessages,
      tools: {
        get_flow,
        tool_call_test_flow
      },
      experimental_toolCallStreaming: true,
      maxSteps: 25,
      onError: (error) => {
        console.error('Error creating flow from chat:', error);
      }
    });

    return response.toDataStreamResponse({
      getErrorMessage: (error: unknown) => {
        if (error instanceof Error) {
          return error.message;
        }
        return 'An unknown error occurred';
      }
    });
    
  } catch (error) {
    console.error('Error creating flow from chat:', error);
    return NextResponse.json(
      { error: 'Failed to create flow' },
      { status: 500 }
    );
  }
} 