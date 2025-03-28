import { verifySignatureAppRouter } from '@upstash/qstash/nextjs';
import { NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_KEY!
);

const BASE_URL = process.env.FRONTEND_URL;

async function handler(req: Request) {
  
  try {
    const body = await req.json();
    
    const { flowId, apiKey } = body;

    if (!flowId || !apiKey) {
      return NextResponse.json({ error: 'Missing required parameters' }, { status: 400 });
    }

    const { data: flow, error: flowError } = await supabase
      .from('user_flows')
      .select('status')
      .eq('id', flowId)
      .single();

    if (flowError) {
      throw new Error(`Failed to get flow status: ${flowError.message}`);
    }

    if (flow.status === 'Draft') {
      return NextResponse.json({ 
        success: true, 
        message: 'Flow is in draft mode, skipping execution' 
      });
    }
    
    const response = await fetch(`${BASE_URL}/api/flow/run-flow`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'VEYRAX_API_KEY': apiKey
      },
      body: JSON.stringify({ flowId })
    });

    const responseBody = await response.text();

    if (!response.ok) {
      throw new Error(`Failed to run flow: ${response.status} ${response.statusText} - ${responseBody}`);
    }

    return NextResponse.json({ success: true });
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