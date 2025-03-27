import { appendResponseMessages, streamText } from 'ai';
import { flowRunPrompt } from '@/app/prompts/flow_run_prompt';
import { createClient } from '@supabase/supabase-js';
import { createOpenRouter } from '@openrouter/ai-sdk-provider';
import { type Message } from 'ai';
import { tool_call_test_flow, get_flow } from '@/lib/ai/tools/tool-call'

const openrouter = createOpenRouter({
  apiKey: process.env.OPENROUTER_API_KEY || ''
});

const modelName = 'anthropic/claude-3.7-sonnet';  

export const maxDuration = 30;

export async function POST(req: Request) {
  console.log('Received request to run-flow');
  
  if (!process.env.NEXT_PUBLIC_SUPABASE_URL || !process.env.SUPABASE_SERVICE_KEY) {
    console.error('Missing Supabase environment variables');
    return new Response('Server configuration error', { status: 500 });
  }

  const supabase = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL,
    process.env.SUPABASE_SERVICE_KEY
  );

  const apiKey = req.headers.get('VEYRAX_API_KEY');
  console.log('API Key present:', !!apiKey);
  
  if (!apiKey) {
    return new Response('API key is required', { status: 401 });
  }

  try {
    const { data: apiKeyData, error: apiKeyError } = await supabase
      .from('users_api_keys')
      .select('user_id')
      .eq('api_key', apiKey)
      .single();

    console.log('API Key validation:', apiKeyError ? 'failed' : 'success');
    
    if (apiKeyError || !apiKeyData) {
      console.error('API Key validation error:', apiKeyError);
      return new Response('Invalid API key', { status: 401 });
    }

    const body = await req.json();
    const { flowId } = body;
    console.log('Flow ID:', flowId);

    const { data: flowData, error: flowError } = await supabase
      .from('user_flows')
      .select('id, name, description, plain_description')
      .eq('id', flowId)
      .eq('user_id', apiKeyData.user_id)
      .single();

    console.log('Flow validation:', flowError ? 'failed' : 'success');
    
    if (flowError || !flowData) {
      console.error('Flow validation error:', flowError);
      return new Response('Flow not found or unauthorized', { status: 403 });
    }

    let flowContextInfo = '';
    if (flowData) {
      flowContextInfo = `
      Current flow information:
      - ID: ${flowData.id}
      - Name: ${flowData.name}
      - Description: ${flowData.plain_description || ''}
      
      This is the flow that the service account wants to test. Use the ID provided above when calling the tool_call_test_flow tool.
      `;
    }

    const messages: Message[] = [
      {
        id: 'test-message-1',
        role: "user",
        content: "What flow you have access to?"
      }
    ];

    console.log('Starting flow test with message:', messages[0].content);

    const SystemMainPrompt = `
      You are a helpful assistant that helps service accounts test automated workflows.
      Your task is to understand the flow and test its functionality.

      ${flowContextInfo}

      You are tester. You main goal is first call get flows, and then call test flow with the id provided.
      
      ${flowData ? 'The service account already has a flow they want to test. Use the current flow ID for testing.' : 'Get flow first, then tool-call to test this out.'}

      ${flowRunPrompt}

      If flow is empty, you should respond with an error message indicating the flow needs to be created first.
    `;

    console.log('SystemMainPrompt:', SystemMainPrompt);

    const result = streamText({
      model: openrouter(modelName) as any,
      messages: [
        { role: 'system', content: SystemMainPrompt, id: 'system' },
        ...messages
      ],
      tools: {
        get_flow,
        tool_call_test_flow
      },
      experimental_toolCallStreaming: true,
      maxSteps: 25,
      experimental_telemetry: { isEnabled: true },
      async onFinish({ response }) {
        console.log('Flow test completed, saving results');
        
        const allMessages = appendResponseMessages({
          messages,
          responseMessages: response.messages,
        });

        const lastAiMessage = allMessages[allMessages.length - 1];
        
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

        // First create a flow run with 'running' status
        const { data: initialFlowRun, error: initialError } = await supabase
          .from('user_flow_runs')
          .insert({
            flow_id: flowId,
            run_status: 'running',
            run_at: new Date().toISOString(),
            payload: {
              message_id: lastAiMessage.id,
              sender: 'assistant',
              message_text: lastAiMessage.content,
              parts: parts,
              metadata: {
                toolInvocations: lastAiMessage.toolInvocations,
                finishReason: null,
                isServiceAccount: true
              }
            }
          })
          .select()
          .single();

        if (initialError) {
          console.error('Initial flow run save error:', initialError);
          throw initialError;
        }

        try {
          const { data: flowRunData, error: flowRunError } = await supabase
            .from('user_flow_runs')
            .update({
              run_status: 'completed',
              completed_at: new Date().toISOString(),
              payload: {
                message_id: lastAiMessage.id,
                sender: 'assistant',
                message_text: lastAiMessage.content,
                parts: parts,
                metadata: {
                  toolInvocations: lastAiMessage.toolInvocations,
                  finishReason: 'success',
                  isServiceAccount: true
                }
              }
            })
            .eq('id', initialFlowRun.id)
            .select();

          if (flowRunError) {
            console.error('Flow run update error:', flowRunError);
            throw flowRunError;
          }

          console.log('Flow run completed successfully:', flowRunData);
        } catch (error) {
          console.error('Error updating flow run:', error);
          await supabase
            .from('user_flow_runs')
            .update({
              run_status: 'failed',
              completed_at: new Date().toISOString(),
              payload: {
                ...initialFlowRun.payload,
                metadata: {
                  ...initialFlowRun.payload.metadata,
                  finishReason: 'error',
                  error: error instanceof Error ? error.message : 'Unknown error occurred'
                }
              }
            })
            .eq('id', initialFlowRun.id);
        }
      }
    });

    console.log('Streaming response back to client');
    return result.toDataStreamResponse({
      getErrorMessage: (error: unknown) => {
        console.error('Error in strea m response:', error);
        if (error instanceof Error) {
          try {
            const errorObj = JSON.parse(error.message);
            if (errorObj.error?.code === 'context_length_exceeded' || 
                errorObj.error?.message?.includes('maximum context length')) {
              return "The conversation is too long. Please start a new flow or try rephrasing your last question more concisely.";
            }
          } catch (e) {
            // If error message isn't JSON, check the raw message
            if (error.message.includes('maximum context length') || 
                error.message.includes('context_length_exceeded')) {
              return "The conversation is too long. Please start a new flow or try rephrasing your last question more concisely.";
            }
          }
          
          if (error.message.includes('ToolInvocation')) {
            return "Error processing tool invocation. Please try again.";
          }
          
          return error.message;
        }
        
        return 'An unknown error occurred';
      }
    });
  } catch (error) {
    console.error('Error in flow run route:', error);
    return new Response('An error occurred while processing your request', { status: 500 });
  }
}
