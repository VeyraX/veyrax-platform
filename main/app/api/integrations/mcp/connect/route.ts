import { NextResponse } from 'next/server';
import { createClient } from '@/lib/utils/supabase/server';

export async function POST(req: Request) {
  try {
    const { repository_id, code, encrypted_api_key } = await req.json();
    
    if (!repository_id) {
      return NextResponse.json(
        { error: 'Repository ID is required' },
        { status: 400 }
      );
    }
    
    const authHeader = req.headers.get('Authorization');
    if (!authHeader && !encrypted_api_key) {
      return NextResponse.json(
        { error: 'Authorization is required' },
        { status: 401 }
      );
    }
    
    const token = encrypted_api_key || authHeader?.replace('Bearer ', '');
    
    const deployUrl = `${process.env.VEYRAX_DEPLOY_BASE_URL}/repo/connect`;
    const response = await fetch(deployUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        repository_id,
        code,
        encrypted_api_key
      })
    });
    
    if (!response.ok) {
      let errorMessage = `Failed to connect MCP container: ${response.statusText}`;
      try {
        const errorData = await response.json();
        return NextResponse.json(
          errorData,
          { status: response.status }
        );
      } catch (e) {
        return NextResponse.json(
          { error: errorMessage },
          { status: response.status }
        );
      }
    }
    
    const data = await response.json();
    return NextResponse.json(data);
    
  } catch (error: any) {
    console.error('Error in MCP connect endpoint:', error);
    return NextResponse.json(
      { error: error.message || 'An unexpected error occurred' },
      { status: 500 }
    );
  }
} 