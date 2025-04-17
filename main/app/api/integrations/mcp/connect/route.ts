import { NextResponse } from 'next/server';
import { createClient } from '@/lib/utils/supabase/server';
import { getUserApiKey } from '@/app/modules/integrations/api/api.integration.mcp.server';
import { validateUserAuthentication } from '@/app/modules/integrations/api/api.integrations.server';

export async function POST(req: Request) {
  try {
    const { repository_id, code, encrypted_api_key, auth_token } = await req.json();
    
    if (!repository_id) {
      return NextResponse.json(
        { error: 'Repository ID is required' },
        { status: 400 }
      );
    }
    
    let token = auth_token;
    let isApiKey = false;
    
    if (encrypted_api_key && code) {
      try {
        const userId = await validateUserAuthentication({
          encrypted_api_key,
          code
        });
        
        if (userId) {
          const apiKey = await getUserApiKey(userId);
          if (apiKey) {
            token = apiKey;
            isApiKey = true; 
          }
        }
      } catch (authError) {
        console.error('Error validating user authentication:', authError);
      }
    }
    
    if (!token) {
      return NextResponse.json(
        { error: 'Authorization is required' },
        { status: 401 }
      );
    }
    
    const deployUrl = `${process.env.VEYRAX_DEPLOY_BASE_URL}/repo/connect`;
    
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    
    if (isApiKey) {
      headers['VEYRAX_API_KEY'] = token;
    } else {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    const response = await fetch(deployUrl, {
      method: 'POST',
      headers,
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