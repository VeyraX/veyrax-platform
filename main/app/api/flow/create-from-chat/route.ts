import { openai } from '@ai-sdk/openai';
import { Message, streamText } from 'ai';
import { NextResponse } from 'next/server';
import { flow_improve_description } from '@/lib/ai/tools/flow-description';
import { getFlowForPrompt, getProviderActionsForFlow } from '@/app/modules/flows/api/api.server.flow';
import { flow_improvement_prompt } from '@/app/prompts/flow_improvements_prompt';
import { flow_builder_prompt } from '@/app/prompts/flow_builder_prompt';
import { tool_call_builder, get_tools } from '@/lib/ai/tools/tool-call';
import { createOpenRouter } from '@openrouter/ai-sdk-provider';
import { getFlowSchedule } from '@/app/modules/flows/api/api.server.schedule.flows';
import { flowScheduleTool, deleteFlowScheduleTool } from '@/lib/ai/tools/flow-schedule';
import { traceModel, generateTraceId } from '@/lib/utils/posthog-tracing';
import { createClient } from '@/lib/utils/supabase/server';
export const maxDuration = 300;

const openrouter = createOpenRouter({
  apiKey: process.env.OPENROUTER_API_KEY || ''
});

const modelName = 'anthropic/claude-3.7-sonnet';

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