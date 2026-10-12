import { Message, streamText, appendResponseMessages } from 'ai';
import { NextResponse } from 'next/server';
import { flow_improve_description } from '@/lib/ai/tools/flow-description';
import { getFlowForPrompt, getProviderActionsForFlow } from '@/app/modules/flows/api/api.server.flow';
import { flow_improvement_prompt } from '@/app/prompts/flow_improvements_prompt';
import { flow_builder_prompt } from '@/app/prompts/flow_builder_prompt';
import { tool_call_builder, get_tools } from '@/lib/ai/tools/tool-call';
import { openrouter, AGENT_MODEL } from '@/lib/ai/openrouter';
import { getFlowSchedule } from '@/app/modules/flows/api/api.server.schedule.flows';
import { flowScheduleTool, deleteFlowScheduleTool } from '@/lib/ai/tools/flow-schedule';
import { traceModel, generateTraceId } from '@/lib/utils/posthog-tracing';
import { createClient } from '@/lib/utils/supabase/server';
import { canUserSendMessageServer } from '@/app/modules/settings/api/api.server.settings';
export const maxDuration = 300;

const modelName = AGENT_MODEL;

export async function POST(request: Request) {
  const clonedReq = request.clone();
  
  try {
    let reqBody;
    try {
      reqBody = await clonedReq.json();
    } catch (error) {
      console.error('Error parsing request body:', error);
      return NextResponse.json(
        { error: 'Invalid JSON in request body' },
        { status: 400 }
      );
    }

    const { messages, flowId, chatId } = reqBody;
    
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

        const supabase = createClient();
        const { data: { user: currentUser } } = await supabase.auth.getUser();
        
        try {
          await supabase
            .from('flows_messages')
            .insert({
              message_id: limitMessageId,
              flow_id: flowId,
              user_id: currentUser?.id,
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
              type: 'create'
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

    let scheduleInfo = 'No schedule set'; 
    if (currentFlowId) {
      try {
        const flowSchedule = await getFlowSchedule(currentFlowId);
        scheduleInfo = flowSchedule ? `Schedule: ${JSON.stringify(flowSchedule)}` : 'No schedule set';
      } catch (error) {
        console.error('Error fetching flow schedule:', error);
        scheduleInfo = 'Error fetching schedule';
      }
    }

    const supabase = createClient();
    
    const { data: { user }, error: userError } = await supabase.auth.getUser();

    if (userError || !user) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }
    const { data: flow } = await getFlowForPrompt(currentFlowId);

    let flowContextInfo = '';
    if (flow) {
      flowContextInfo = `
      Current flow information:
      - ID: ${flow.id}
      - Name: ${flow.name}
      - Description: ${flow.plain_description || ''}
      - ${scheduleInfo}
      
      This is the flow that user wants to test. Use the ID provided above when calling the tool_call_test_flow tool.
      `;
    }

    const { data: actions, error } = await getProviderActionsForFlow();

    const SystemMainPrompt = `
      You are a helpful assistant that helps users create automated workflows.
      Your task is to understand the user's request and convert it into a structured workflow.

      ${flow_improvement_prompt}
      ${flowContextInfo}
      ${scheduleInfo}

      Available actions:
      ${actions.map((action: any) => `- ${action.action_slug} (Provider: ${action.provider_name}, provider_tag: ${action.provider_tag}, Logo URL: ${action.logo_url}). Input schema: ${JSON.stringify(action.input_schema)}.`).join('\n')}

      ${flow_builder_prompt}
      Never add title to the flow description. Start with text and description, bullect points. No titles.

      You MUST generate HTML for each action to fit the flow. MUST.

      Try to convince user use ID of their entities in the flow, not in the right time. Ask user about IDs and propose help if user doesn't remember.

      Because it will redundant work find ID all the time if we can specify it right away.
    `;

    const allMessages = [
      { role: 'system', content: SystemMainPrompt, id: 'system' },
      ...messages
    ];

    let model = openrouter(modelName) as any;
    
    const traceId = generateTraceId();
    
    model = traceModel(model, user.id, {
      trace_id: traceId,
      flow_id: currentFlowId,
      endpoint: 'flow-create',
      user_email: user.email
    });

    const lastUserMessage = messages[messages.length - 1];
    const userMessageId = `usr-${Date.now()}-${Math.random().toString(36).substring(2, 10)}`;

    const response = streamText({
      model: model,
      messages: allMessages,
      tools: {
        flow_improve_description,
        tool_call_builder
      },
      experimental_toolCallStreaming: true,
      maxSteps: 25,
      onError: (error) => {
        console.error('Error creating flow from chat:', error);
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
                  type: 'create'
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
                  type: 'create'
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
          if (error.message.includes('context_length_exceeded') || 
              error.message.includes('maximum context length')) {
            return "The workflow description is too long. Please simplify your requirements or split them into smaller workflows.";
          }
          
          if (error.message.includes('rate_limit')) {
            return "We're experiencing high demand. Please try again in a few moments.";
          }
          
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