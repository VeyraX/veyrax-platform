import { verifySignatureAppRouter } from '@upstash/qstash/nextjs';
import { NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_KEY!
);

const BASE_URL = process.env.FRONTEND_URL;
const ACI_SERVER_URL = process.env.ACI_SERVER_URL || 'http://localhost:8000';

async function handler(req: Request) {
  
  try {
    const body = await req.json();
    
    const { flowId, apiKey, allowDraft } = body;

    if (!flowId || !apiKey) {
      return NextResponse.json({ error: 'Missing required parameters' }, { status: 400 });
    }

    const { data: apiKeyData, error: apiKeyError } = await supabase
      .from('users_api_keys')
      .select('user_id')
      .eq('api_key', apiKey)
      .single();
      
    if (apiKeyError || !apiKeyData) {
      return NextResponse.json({ error: 'Invalid API key' }, { status: 401 });
    }
    
    const { data: flow, error: flowError } = await supabase
      .from('user_flows')
      .select('id, name, description, plain_description, user_id, status')
      .eq('id', flowId)
      .eq('user_id', apiKeyData.user_id)
      .single();

    if (flowError) {
      throw new Error(`Failed to get flow status: ${flowError.message}`);
    }

    if (flow.status === 'Draft' && !allowDraft) {
      return NextResponse.json({ 
        success: true, 
        message: 'Flow is in draft mode, skipping execution' 
      });
    }
    
    const { data: initialFlowRun, error: initialError } = await supabase
      .from('user_flow_runs')
      .insert({
        flow_id: flowId,
        run_status: 'running',
        run_at: new Date().toISOString(),
      })
      .select()
      .single();

    if (initialError) {
      console.error('Initial flow run save error:', initialError);
      throw initialError;
    }
    
    // Call the flow agent route directly
    const response = await fetch(`${ACI_SERVER_URL}/flow/run-flow/${flowId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'VEYRAX_API_KEY': apiKey,
        'X-Flow-Run-ID': initialFlowRun.id
      },
      body: JSON.stringify({ 
        query: "Run the flow automatically triggered by qstash",
        include_debug_info: true
      })
    });

    const responseBody = await response.text();
    let parsedResponse;
    
    try {
      parsedResponse = JSON.parse(responseBody);
    } catch (e) {
      parsedResponse = { error: 'Invalid JSON response', raw: responseBody };
    }

    if (!response.ok) {
      await supabase
        .from('user_flow_runs')
        .update({
          run_status: 'failed',
          completed_at: new Date().toISOString(),
          payload: {
            message_id: `qstash-error-${Date.now()}`,
            sender: 'system',
            message_text: `Failed to run flow: ${response.status} ${response.statusText}`,
            parts: [],
            metadata: {
              finishReason: 'error',
              error: `Failed to run flow: ${response.status} ${response.statusText} - ${responseBody}`
            }
          }
        })
        .eq('id', initialFlowRun.id);
        
      throw new Error(`Failed to run flow: ${response.status} ${response.statusText} - ${responseBody}`);
    }

    // We don't need to update flow run status here as the agent handles it

    return NextResponse.json({ 
      success: true, 
      flowRunId: initialFlowRun.id,
      agentResponse: parsedResponse
    });
  } catch (error) {
    console.error('Detailed error in QStash webhook:', {
      error: error instanceof Error ? error.message : 'Unknown error',
      stack: error instanceof Error ? error.stack : undefined,
      type: error instanceof Error ? error.constructor.name : typeof error
    });
    
    return NextResponse.json({ 
      error: 'Internal server error',
      details: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 });
  }
}

export const POST = verifySignatureAppRouter(handler);

export const runtime = 'edge';
export const dynamic = 'force-dynamic'; 