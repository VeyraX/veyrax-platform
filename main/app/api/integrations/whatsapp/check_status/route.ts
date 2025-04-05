import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@/lib/utils/supabase/server';
import { createClient as createServiceClient } from '@supabase/supabase-js';
import { validateUserAuthentication } from '@/app/modules/integrations/api/api.integrations.server';

export async function POST(request: NextRequest) {
  try {
    const requestData = await request.json();
    const { encrypted_api_key, code, user_id } = requestData;
    
    let headers: Record<string, string> = {};
    let userId = user_id;
    let supabase;
    
    if (encrypted_api_key) {
      try {
        userId = await validateUserAuthentication({
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
          .eq('id', userId)
          .single();
          
        if (userData?.api_key) {
          headers = {
            'VEYRAX-API-KEY': userData.api_key
          };
        }
      } catch (authError) {
        console.error('Auth error with API key:', authError);
        return NextResponse.json({
          success: false,
          message: 'Authentication failed'
        }, { status: 401 });
      }
    } else if (user_id) {
      supabase = createServiceClient(
        process.env.SUPABASE_URL!,
        process.env.SUPABASE_SERVICE_KEY!
      );
      
      const { data: userData } = await supabase
        .from('users_api_keys')
        .select('api_key')
        .eq('id', userId)
        .single();
        
      if (userData?.api_key) {
        headers = {
          'VEYRAX-API-KEY': userData.api_key
        };
      } else {
        return NextResponse.json({
          success: false,
          message: 'API key not found for the specified user'
        }, { status: 401 });
      }
    } else {
      supabase = createClient();
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session) {
        return NextResponse.json(
          { success: false, message: 'Authentication required' },
          { status: 401 }
        );
      }
      
      userId = session.user.id;
      headers = {
        'Authorization': `Bearer ${session.access_token}`
      };
    }

    // Call the WhatsApp check_status API endpoint
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/whatsapp/check_status`, {
      method: 'POST',
      headers: {
        ...headers,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        user_id: userId
      }),
      credentials: 'include'
    });

    if (!response.ok) {
      const errorText = await response.text();
      return NextResponse.json(
        { success: false, message: `WhatsApp status check failed: ${errorText}` },
        { status: response.status }
      );
    }

    const data = await response.json();
    
    // Return the login status and phone number if available
    return NextResponse.json({
      success: true,
      data: {
        is_logged_in: data.data?.is_logged_in || false,
        phone: data.data?.phone,
      },
      message: data.message || 'Status check completed'
    });
  } catch (error) {
    console.error('Error checking WhatsApp status:', error);
    return NextResponse.json(
      { success: false, message: error instanceof Error ? error.message : 'An unexpected error occurred' },
      { status: 500 }
    );
  }
} 