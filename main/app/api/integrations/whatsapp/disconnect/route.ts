import { NextRequest, NextResponse } from 'next/server';
import { validateUserAuthentication, saveDisconnectWhatsapp } from '@/app/modules/integrations/api/api.integrations.server';
import { createClient } from '@/lib/utils/supabase/server';
import { createClient as createServiceClient } from '@supabase/supabase-js';

export async function POST(request: NextRequest) {
  try {
    const requestData = await request.json();
    const { user_id, encrypted_api_key, code } = requestData;
    
    let headers: Record<string, string> = {};
    let userId = user_id;
    let supabase;

  
    supabase = createClient();
    const { data: { session } } = await supabase.auth.getSession();
    
    if (session) {
      headers = {
        'Authorization': `Bearer ${session.access_token}`
      };
    }
    
    if (encrypted_api_key) {
      try {
        userId = await validateUserAuthentication({
          encrypted_api_key,
          code
        });
        
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
        }
      } catch (authError) {
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

    try {
      userId = await validateUserAuthentication({
        user_id,
        encrypted_api_key,
        code
      });
    } catch (authError: any) {
      return NextResponse.json({ 
        success: false, 
        error: authError.message 
      }, { status: 401 });
    }

    try {
      await saveDisconnectWhatsapp({
        user_id: userId,
        access_token: session?.access_token
      });

      return NextResponse.json({
        success: true,
        message: 'WhatsApp disconnected successfully'
      });
    } catch (error: any) {
      return NextResponse.json({ 
        success: false, 
        error: error.message 
      }, { status: 500 });
    }
  } catch (error) {
    return NextResponse.json(
      { success: false, message: error instanceof Error ? error.message : 'An unexpected error occurred' },
      { status: 500 }
    );
  }
} 