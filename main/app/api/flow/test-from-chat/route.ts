import { openai } from '@ai-sdk/openai';
import { Message, streamText } from 'ai';
import { NextResponse } from 'next/server';
import { tool_call_test_flow, get_flows } from '@/lib/ai/tools/tool-call'
import { getFlowForPrompt } from '@/app/modules/flows/api/api.server.flow';

export async function POST(request: Request) {
  try {
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
      You are a helpful assistant that helps users create automated workflows.
      Your task is to understand the user's request and convert it into a structured workflow.

      ${flowContextInfo}

      You are tester. You main goal is first call get flows, and then call test flow with the id that user choose.
      
      ${flow ? 'The user already has a flow they want to test. Use the current flow ID for testing.' : 'Get flow first, then tool-call to test this out.'}
    `;

    const allMessages = [
      { role: 'system', content: SystemMainPrompt, id: 'system' },
      ...messages
    ];

    const response = streamText({
      model: openai('gpt-4o'),
      messages: allMessages,
      tools: {
        get_flows,
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