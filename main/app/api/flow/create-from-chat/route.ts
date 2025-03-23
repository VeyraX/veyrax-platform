import { createClient } from '@/lib/utils/supabase/server';
import { openai } from '@ai-sdk/openai';
import { Message, streamText } from 'ai';
import { NextResponse } from 'next/server';
import { flow_improve_description } from '@/lib/ai/tools/flow-description';

export async function POST(request: Request) {
  try {
    const { messages, chatId } = await request.json();
    
    if (!messages || messages.length === 0) {
      return NextResponse.json(
        { error: 'No messages provided' },
        { status: 400 }
      );
    }
    
    const supabase = createClient();
    const { data: actions, error } = await supabase
      .from('provider_actions')
      .select('provider_id, provider_name, action_name, logo_url');
    
    if (error) {
      return NextResponse.json(
        { error: 'Failed to fetch available actions' },
        { status: 500 }
      );
    }

    const systemMessage = `
      You are a helpful assistant that helps users create automated workflows.
      Your task is to understand the user's request and convert it into a structured workflow.
      
      Available actions:
      ${actions.map(action => 
        `- ${action.action_name} (Provider: ${action.provider_name})`
      ).join('\n')}
      
      When creating a workflow, follow these guidelines:
      1. Create a concise but descriptive name for the workflow
      2. Generate a detailed step-by-step description that explains how the workflow operates
      3. Mention specific actions from the available actions list when appropriate
      4. Include necessary triggers, conditions, and actions
      
      You should use the flow_improve_description tool to create workflow details based on the user's request.
      Only return plain text responses if the user is asking questions about workflows or if you need more information.
      If the user provides enough information to create a workflow, use the tool instead of responding with text.
    `;

    const allMessages = [
      { role: 'system', content: systemMessage, id: 'system' },
      ...messages
    ];

    const response = streamText({
      model: openai('gpt-4o'),
      messages: allMessages,
      tools: {
        flow_improve_description
      },
      experimental_toolCallStreaming: true,
      maxSteps: 3
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