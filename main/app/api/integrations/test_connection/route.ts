import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@/lib/utils/supabase/server';
import { createClient as createServiceClient } from '@supabase/supabase-js';
import { validateUserAuthentication } from '@/app/modules/integrations/api/api.integrations.server';
import { getAuthHeaders } from '@/lib/actions/actions';

export async function POST(request: NextRequest) {
  try {
    const { providerTag, dbConfig, encrypted_api_key, code } = await request.json();
    
    if (!providerTag || !dbConfig) {
      return NextResponse.json({ 
        data: {
          success: false,
          message: 'Missing required parameters'
        }
      });
    }
    
    let headers = {};
    
    if (encrypted_api_key) {
      try {
        const user_id = await validateUserAuthentication({
          encrypted_api_key,
          code
        });
        
        const supabase = createServiceClient(
          process.env.SUPABASE_URL!,
          process.env.SUPABASE_SERVICE_KEY!
        );
        
        const { data: userData } = await supabase
          .from('users_api_keys')
          .select('api_key')
          .eq('id', user_id)
          .single();
          
        if (userData?.api_key) {
          headers = {
            'VEYRAX_API_KEY': userData.api_key
          };
        }
      } catch (authError) {
        console.error('Auth error with API key:', authError);
        return NextResponse.json({
          data: {
            success: false,
            message: 'Authentication failed'
          }
        }, { status: 401 });
      }
    } else {
      headers = await getAuthHeaders();
    }
    
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const response = await fetch(`${backendUrl}/${providerTag}/test_connection`, {
      method: 'POST',
      headers: {
        ...headers,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(dbConfig),
      credentials: 'include'
    });
    
    const responseData = await response.json();
    
    return NextResponse.json({
      data: {
        success: responseData.data?.success || false,
        message: responseData.data?.message || 'Connection test completed'
      }
    });
  } catch (error) {
    console.error('Error in test_connection API route:', error);
    return NextResponse.json({ 
      data: {
        success: false,
        message: error instanceof Error ? error.message : 'Failed to test connection'
      }
    });
  }
}