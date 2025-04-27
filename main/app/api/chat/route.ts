import { createOpenRouter } from '@openrouter/ai-sdk-provider';
import { appendResponseMessages, streamText } from 'ai';
import { getUserTools } from '@/lib/utils/get-user-tools';
import { main_system_prompt } from '../../prompts/main_system_prompt';
import { createClient } from '@/lib/utils/supabase/server';
import { tools } from '@/lib/ai/tools';
import { traceModel, generateTraceId } from '@/lib/utils/posthog-tracing';
import { canUserSendMessageServer } from '@/app/modules/settings/api/api.server.settings';

export const maxDuration = 150;

const openrouter = createOpenRouter({
  apiKey: process.env.OPENROUTER_API_KEY || '',
});
const modelName = 'openai/gpt-4.1';

export async function POST(req: Request) {
  const clonedReq = req.clone();
  
  try {
    const supabase = createClient();
    
    const { data: { user }, error: userError } = await supabase.auth.getUser();
    
    if (userError || !user) {
      return new Response('Unauthorized', { status: 401 });
    }

    let body;
    try {
      body = await clonedReq.json();
    } catch (error) {
      console.error('Error parsing request body:', error);
      return new Response('Invalid JSON in request body', { status: 400 });
    }
    
    const { messages, chatId } = body;

    if (!messages || !Array.isArray(messages)) {
      return new Response('Invalid messages format', { status: 400 });
    }
    
    if (messages.length > 0 && messages[messages.length - 1].role === 'user') {
      const messageCheck = await canUserSendMessageServer();
      
      if (!messageCheck.allowed) {
        const limitMessageId = `msg-limit-${Date.now()}`;
        
        const upgradeMessage = `📣 **Message limit reached**

You've reached the limit of ${messageCheck.limit} messages on your current plan.

To continue using the chat, please upgrade your plan at [veyrax.com/pricing](https://veyrax.com/pricing) to get more messages.`;
        
        try {
          await supabase
            .from('chats_messages')
            .insert({
              message_id: limitMessageId,
              chat_id: chatId,
              sender: 'system',
              message_text: upgradeMessage,
              parts: [{
                type: 'text',
                text: upgradeMessage
              }],
              metadata: {
                isLimitMessage: true,
                current: messageCheck.current,
                limit: messageCheck.limit
              }
            });
        } catch (error) {
          console.error('Error saving limit message to database:', error);
        }
        
        return new Response(
          JSON.stringify({
            error: {
              message: 'MESSAGE_LIMIT_EXCEEDED',
              details: {
                limitMessage: upgradeMessage,
                messageId: limitMessageId,
                current: messageCheck.current,
                limit: messageCheck.limit,
                needsUpgrade: messageCheck.needsUpgrade
              }
            }
          }),
          { 
            status: 400,
            headers: { 'Content-Type': 'application/json' }
          }
        );
      }
    }

    const userTools = await getUserTools();
    
    const customSystemPrompt = `${main_system_prompt}\n\nUser has access to the following tools: ${JSON.stringify(userTools)}`;

    let model = openrouter(modelName);
    
    const traceId = generateTraceId();
    
    model = traceModel(model, user.id, {
      trace_id: traceId,
      chat_id: chatId,
      user_email: user.email,
      endpoint: 'chat'
    });

    const result = streamText({
      model: model,
      messages,
      system: customSystemPrompt,
      tools: tools,
      experimental_toolCallStreaming: true,
      maxSteps: 25,
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

        try {
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
        } catch (error) {
          console.error('Error saving message to Supabase:', error);
        }
      }
    });

    return result.toDataStreamResponse({
      getErrorMessage: (error: unknown) => {
        if (error instanceof Error) {
          let errorMessage = error.message;
          try {
            const errorObj = JSON.parse(errorMessage);
            if (errorObj.error?.code === 'context_length_exceeded' || 
                errorObj.error?.message?.includes('maximum context length')) {
              return "The conversation is too long. Please start a new chat or try rephrasing your last question more concisely.";
            }
          } catch (e) {
            if (errorMessage.includes('maximum context length') || 
                errorMessage.includes('context_length_exceeded')) {
              return "The conversation is too long. Please start a new chat or try rephrasing your last question more concisely.";
            }
          }
          
          if (errorMessage.includes('ToolInvocation')) {
            return "Error processing tool invocation. Please try again.";
          }
          
          return errorMessage;
        }
        
        return 'An unknown error occurred';
      }
    });
  } catch (error) {
    console.error('Error in chat route:', error);
    return new Response('An error occurred while processing your request', { status: 500 });
  }
}