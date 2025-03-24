import { openai } from '@ai-sdk/openai';
import { Message, streamText } from 'ai';
import { NextResponse } from 'next/server';
import { flow_improve_description } from '@/lib/ai/tools/flow-description';
import { getProviderActionsForFlow } from '@/app/modules/flows/api/api.server.flow';
import { flow_improvement_prompt } from '@/app/prompts/flow_improvements_prompt';


export async function POST(request: Request) {
  try {
    const { messages, chatId } = await request.json();
    
    if (!messages || messages.length === 0) {
      return NextResponse.json(
        { error: 'No messages provided' },
        { status: 400 }
      );
    }

    const { data: actions, error } = await getProviderActionsForFlow();

    const SystemMainPrompt = `
      You are a helpful assistant that helps users create automated workflows.
      Your task is to understand the user's request and convert it into a structured workflow.

      ${flow_improvement_prompt}

      Available actions:
      ${actions.map((action: any) => `- ${action.action_name} (Provider: ${action.provider_name}, Logo URL: ${action.logo_url})`).join('\n')}


      Never add title to the flow description. Start with text and description, bullect points. No titles.
    `;


    const allMessages = [
      { role: 'system', content: SystemMainPrompt, id: 'system' },
      ...messages
    ];

    const response = streamText({
      model: openai('gpt-4o'),
      messages: allMessages,
      tools: {
        flow_improve_description
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