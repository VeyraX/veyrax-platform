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
          .eq('user_id', userId)
          .single();
          
        if (userData?.api_key) {
          headers = {
            'VEYRAX_API_KEY': userData.api_key
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
        .eq('user_id', userId)
        .single();
        
      if (userData?.api_key) {
        headers = {
          'VEYRAX_API_KEY': userData.api_key
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

    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/whatsapp/authenticate`, {
      method: 'POST',
      headers: {
        ...headers,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        include_component: false,
        include_qr_ascii: false,
        user_id: userId
      }),
      credentials: 'include'
    });

    console.log('headers', headers);

    if (!response.ok) {
      const errorText = await response.text();
      return NextResponse.json(
        { success: false, message: `WhatsApp authentication failed: ${errorText}` },
        { status: response.status }
      );
    }

    const data = await response.json();

    return NextResponse.json({
      success: true,
      data: {
        qr_image_base64: data.data?.qr_image_base64,
        is_logged_in: data.data?.is_logged_in,
      },
      message: data.message || 'Authentication process started'
    });
  } catch (error) {
    console.error('Error authenticating WhatsApp:', error);
    return NextResponse.json(
      { success: false, message: error instanceof Error ? error.message : 'An unexpected error occurred' },
      { status: 500 }
    );
  }
} 