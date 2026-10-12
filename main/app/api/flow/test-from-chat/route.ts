import { Message, streamText, appendResponseMessages } from 'ai';
import { NextResponse } from 'next/server';
import { tool_call_test_flow, get_flow } from '@/lib/ai/tools/tool-call'
import { getFlowForPrompt } from '@/app/modules/flows/api/api.server.flow';
import { flow_testing_prompt } from '@/app/prompts/flow_testing_prompt';
import { openrouter, AGENT_MODEL } from '@/lib/ai/openrouter';
import { createClient } from '@/lib/utils/supabase/server';
import { traceModel, generateTraceId } from '@/lib/utils/posthog-tracing';
import { canUserSendMessageServer } from '@/app/modules/settings/api/api.server.settings';

export const maxDuration = 150;

const modelName = AGENT_MODEL;

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
    
    if (messages.length > 0 && messages[messages.length - 1].role === 'user') {
      const messageCheck = await canUserSendMessageServer();
      
      if (!messageCheck.allowed) {
        const limitMessageId = `msg-limit-${Date.now()}`;
        
        const upgradeMessage = `📣 **Message limit reached**

You've reached the limit of ${messageCheck.limit} messages on your current plan.

To continue using the chat, please upgrade your plan at [veyrax.com/pricing](https://veyrax.com/pricing) to get more messages.`;
        
        try {
          await supabase
            .from('flows_messages')
            .insert({
              message_id: limitMessageId,
              flow_id: flowId,
              user_id: user.id,
              sender: 'system',
              message_text: upgradeMessage,
              parts: [{
                type: 'text',
                text: upgradeMessage
              }],
              metadata: JSON.stringify({
                isLimitMessage: true,
                current: messageCheck.current,
                limit: messageCheck.limit
              }),
              type: 'test'
            });
        } catch (error) {
          console.error('Error saving limit message to database:', error);
        }
        
        return NextResponse.json(
          {
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
          },
          { status: 400 }
        );
      }
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

    const lastUserMessage = messages[messages.length - 1];
    const userMessageId = `usr-${Date.now()}-${Math.random().toString(36).substring(2, 10)}`;

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
        console.error('Error testing flow from chat:', error);
      },
      async onFinish({ response }) {
        if (lastUserMessage && lastUserMessage.role === 'user') {
          try {
            const allMessages = appendResponseMessages({
              messages,
              responseMessages: response.messages,
            });
            
            const lastAiMessage = allMessages[allMessages.length - 1];
            const assistantMessageId = `ast-${Date.now()}-${Math.random().toString(36).substring(2, 10)}`;
            
            const parts = [];
            
            if (lastAiMessage.toolInvocations) {
              for (const invocation of lastAiMessage.toolInvocations) {
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
            
            if (lastAiMessage.content) {
              parts.push({
                type: 'text',
                text: lastAiMessage.content
              });
            }
            
            const supabase = createClient();
            
            try {
              await supabase
                .from('flows_messages')
                .insert({
                  message_id: userMessageId,
                  flow_id: currentFlowId,
                  user_id: user.id,
                  sender: 'user',
                  message_text: lastUserMessage.content,
                  parts: [{
                    type: 'text',
                    text: lastUserMessage.content
                  }],
                  type: 'test'
                });
              
              
              await supabase
                .from('flows_messages')
                .insert({
                  message_id: assistantMessageId,
                  flow_id: currentFlowId,
                  user_id: user.id,
                  sender: 'assistant',
                  message_text: lastAiMessage.content || '',
                  parts: parts,
                  metadata: JSON.stringify({
                    toolInvocations: lastAiMessage.toolInvocations,
                    finishReason: null
                  }),
                  type: 'test'
                });
            } catch (dbError) {
              console.error('Error saving to flows_messages:', dbError);
            }
              
          } catch (error) {
            console.error('Error processing messages for flows_messages:', error);
          }
        }
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
    console.error('Error testing flow from chat:', error);
    return NextResponse.json(
      { error: 'Failed to test flow' },
      { status: 500 }
    );
  }
} 