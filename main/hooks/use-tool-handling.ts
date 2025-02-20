import { type Message } from 'ai/react';
import { createChatMessage } from "@/app/modules/agent/components/api/api.agent";

interface ExtendedMessage extends Message {
  toolCalls?: any[];
  toolResults?: any[];
  toolInvocations?: any[];
  finishReason?: string;
}

export function useToolHandling(chatId: string | null) {
  const handleToolProcessing = async (message: ExtendedMessage) => {
    if (message.role === 'assistant') {
      if (!chatId) {
        console.error('No chatId provided for message:', message.id);
        return;
      }

      try {
        console.log('Starting to process assistant message:', {
          messageId: message.id,
          chatId: chatId
        });
        
        const metadata = {
          toolInvocations: message.toolInvocations?.map(ti => ({
            toolCallId: ti.toolCallId,
            toolName: ti.toolName,
            args: ti.args,
            state: ti.state,
            result: ti.result || undefined
          })),
          finishReason: message.finishReason
        };
        
        console.log('Saving assistant message to database:', {
          messageId: message.id,
          chatId: chatId,
          contentLength: message.content.length
        });

        await createChatMessage({
          message_id: message.id,
          chat_id: chatId,
          sender: 'assistant',
          message_text: message.content,
          parts: message.parts?.map(p => {
            if (p.type === 'reasoning') {
              return {
                type: 'text',
                text: p.reasoning
              };
            }
            return {
              type: p.type === 'tool-invocation' ? 'tool-invocation' : 'text',
              ...(p.type === 'text' ? { text: p.text } : {}),
              ...(p.type === 'tool-invocation' ? {
                toolInvocation: {
                  toolCallId: p.toolInvocation.toolCallId,
                  toolName: p.toolInvocation.toolName,
                  args: p.toolInvocation.args
                }
              } : {})
            };
          }),
          metadata: {
            toolInvocations: metadata.toolInvocations,
            finishReason: metadata.finishReason
          }
        });

        console.log('Successfully saved assistant message to database:', {
          messageId: message.id,
          chatId: chatId
        });
      } catch (error) {
        console.error('Error saving assistant message:', {
          messageId: message.id,
          chatId: chatId,
          error: error
        });
      }
    }
  };

  return { handleToolProcessing };
}