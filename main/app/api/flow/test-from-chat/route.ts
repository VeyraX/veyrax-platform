import { openai } from '@ai-sdk/openai';
import { Message, streamText } from 'ai';
import { NextResponse } from 'next/server';
import { tool_call_test_flow, get_flow } from '@/lib/ai/tools/tool-call'
import { getFlowForPrompt } from '@/app/modules/flows/api/api.server.flow';
import { flow_testing_prompt } from '@/app/prompts/flow_testing_prompt';
import { createOpenRouter } from '@openrouter/ai-sdk-provider';
import { createClient } from '@/lib/utils/supabase/server';
import { traceModel, generateTraceId } from '@/lib/utils/posthog-tracing';

export const maxDuration = 150;

const openrouter = createOpenRouter({
  apiKey: process.env.OPENROUTER_API_KEY || ''
});

const modelName = 'anthropic/claude-3.7-sonnet';

export async function POST(request: Request) {
  try {
    const supabase = createClient();
    const { data: { user }, error: userError } = await supabase.auth.getUser();

    if (userError || !user) {
      console.error('User not found');
      return new Response('User not found', { status: 401 });
    }

    const { messages, chatId, flowId } = await request.json();
    
    if (!messages || messages.length === 0) {
      return NextResponse.json(
        { error: 'No messages provided' },
        { status: 400 }
      );
    }

    let currentFlowId = flowId;

    if (!currentFlowId && chatId) {
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
      
      This is the flow that user wants to test. Use the ID provided above when calling the tool_call_test_flow tool.
      `;
    }

    const SystemMainPrompt = `
      You are a helpful assistant that helps users test automated workflows.
      Your task is to understand the flow and test its functionality.

      ${flowContextInfo}

      You are tester. You main goal is first call get flows, and then call test flow with the id that user choose.
      
      ${flow ? `The user already has a flow they want to test. Use the current flow ID for testing.` : 'Get flow first, then tool-call to test this out.'}

      ${flow_testing_prompt}

      If flow is empty, you should ask user to create a flow first.

      It is VERY important to use the same param and methods and args that you have received from the get_flow tool.

      It is VERY important.

      For example, if provider slug is "google-calendar" it means that you should use the google-calendar tool, and methods as action_slug. 
    `;

    const allMessages = [
      { role: 'system', content: SystemMainPrompt, id: 'system' },
      ...messages
    ];
    const traceId = generateTraceId();

    const model = traceModel(openrouter(modelName) as any, user.id, {
      trace_id: traceId,
      flow_id: currentFlowId,
      user_email: user.email,
      endpoint: 'flow-test'
    });

    const response = streamText({
      model: model,
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