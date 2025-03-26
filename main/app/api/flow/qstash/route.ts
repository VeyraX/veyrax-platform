import { verifySignatureAppRouter } from '@upstash/qstash/nextjs';
import { NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_KEY!
);

const BASE_URL = process.env.FRONTEND_URL;

async function handler(req: Request) {
  console.log('🚀 QStash webhook received');
  
  try {
    console.log('Parsing request body...');
    const body = await req.json();
    console.log('Request body:', JSON.stringify(body, null, 2));
    
    const { flowId, apiKey } = body;
    console.log('FlowId:', flowId);
    console.log('API Key present:', !!apiKey);

    if (!flowId || !apiKey) {
      console.error('Missing parameters - flowId:', !flowId, 'apiKey:', !apiKey);
      return NextResponse.json({ error: 'Missing required parameters' }, { status: 400 });
    }
    
    console.log('Making request to run-flow endpoint...');
    console.log('Target URL:', `${BASE_URL}/api/flow/run-flow`);
    
    const response = await fetch(`${BASE_URL}/api/flow/run-flow`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'VEYRAX_API_KEY': apiKey
      },
      body: JSON.stringify({ flowId })
    });

    console.log('Run-flow response status:', response.status);
    const responseBody = await response.text();
    console.log('Run-flow response body:', responseBody);

    if (!response.ok) {
      console.error('Failed to run flow:', {
        status: response.status,
        statusText: response.statusText,
        body: responseBody
      });
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

export const config = {
  api: {
    bodyParser: false,
  },
}; 