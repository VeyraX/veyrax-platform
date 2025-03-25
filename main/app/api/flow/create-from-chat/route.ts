import { openai } from '@ai-sdk/openai';
import { Message, streamText } from 'ai';
import { NextResponse } from 'next/server';
import { flow_improve_description } from '@/lib/ai/tools/flow-description';
import { getFlowForPrompt, getProviderActionsForFlow } from '@/app/modules/flows/api/api.server.flow';
import { flow_improvement_prompt } from '@/app/prompts/flow_improvements_prompt';
import { flow_builder_prompt } from '@/app/prompts/flow_builder_prompt';
import { tool_call_builder, get_tools } from '@/lib/ai/tools/tool-call';


export async function POST(request: Request) {
  try {
    const { messages, flowId, chatId } = await request.json();
    
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

    const { data: actions, error } = await getProviderActionsForFlow();

    const SystemMainPrompt = `
      You are a helpful assistant that helps users create automated workflows.
      Your task is to understand the user's request and convert it into a structured workflow.

      ${flow_improvement_prompt}
      ${flowContextInfo}

      Available actions:
      ${actions.map((action: any) => `- ${action.action_slug} (Provider: ${action.provider_name}, Logo URL: ${action.logo_url}). Input schema: ${action.input_schema}. Examples: ${action.examples}.`).join('\n')}

      ${flow_builder_prompt}
      Never add title to the flow description. Start with text and description, bullect points. No titles.

      You MUST generate HTML for each action to fit the flow. MUST.
    `;


    const allMessages = [
      { role: 'system', content: SystemMainPrompt, id: 'system' },
      ...messages
    ];

    const response = streamText({
      model: openai('gpt-4o'),
      messages: allMessages,
      tools: {
        flow_improve_description,
        tool_call_builder
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