import { openai } from '@ai-sdk/openai';
import { appendResponseMessages, streamText } from 'ai';
import { getUserTools } from '@/lib/utils/get-user-tools';
import { main_system_prompt } from '../../prompts/main_system_prompt';
import { createClient } from '@/lib/utils/supabase/server';
import { tools } from '@/lib/ai/tools';

export const maxDuration = 30;

export async function POST(req: Request) {
  const supabase = createClient();
  
  const { data: { user }, error: userError } = await supabase.auth.getUser();
  
  if (userError || !user) {
    return new Response('Unauthorized', { status: 401 });
  }

  const body = await req.json();
  const { messages, chatId } = body;

  try {
    const userTools = await getUserTools();
    
    const customSystemPrompt = `${main_system_prompt}\n\nUser has access to the following tools: ${JSON.stringify(userTools)}`;

    const result = streamText({
      model: openai('gpt-4o'),
      messages,
      system: customSystemPrompt,
      tools: tools,
      experimental_toolCallStreaming: true,
      maxSteps: 25,
      experimental_telemetry: { isEnabled: true },
      async onFinish({ response }) {
        const allMessages = appendResponseMessages({
          messages,
          responseMessages: response.messages,
        });

        const lastAiMessage = allMessages[allMessages.length - 1];
        
        const parts = [];
        
        if (lastAiMessage.toolInvocations) {
          for (const invocation of lastAiMessage.toolInvocations) {{
              parts.push({
                type: 'tool-invocation',
                toolInvocation: {
                  toolCallId: invocation.toolCallId,
                  toolName: invocation.toolName,
                  args: invocation.args
                }
              });
            }
          }
        }

        if (lastAiMessage.content) {
          parts.push({
            type: 'text',
            text: lastAiMessage.content
          });
        }

        await supabase
          .from('chats_messages')
          .insert({
            message_id: lastAiMessage.id,
            chat_id: chatId,
            sender: 'assistant',
            message_text: lastAiMessage.content,
            parts: parts,
            metadata: {
              toolInvocations: lastAiMessage.toolInvocations,
              finishReason: null
            }
          });
      }
    });

    return result.toDataStreamResponse({
      getErrorMessage: (error: unknown) => {
        if (error instanceof Error && error.message.includes('maximum context length')) {
          const truncatedMessages = messages.slice(0, -1);
          return "Token limit exceeded. Please try rephrasing your last question more concisely.";
        }
        
        if (error instanceof Error && error.message.includes('ToolInvocation')) {
          return "Error processing tool invocation. Please try again.";
        }
        
        return error instanceof Error ? error.message : 'An unknown error occurred';
      }
    });
  } catch (error) {
    console.error('Error in chat route:', error);
    return new Response('An error occurred while processing your request', { status: 500 });
  }
}