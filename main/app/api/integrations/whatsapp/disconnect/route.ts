import { NextRequest, NextResponse } from 'next/server';
import { validateUserAuthentication, saveDisconnectWhatsapp } from '@/app/modules/integrations/api/api.integrations.server';

export async function POST(request: NextRequest) {
  try {
    const requestData = await request.json();
    const { user_id, encrypted_api_key, code } = requestData;

    let userId;
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
        user_id: userId
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
    console.error('Error disconnecting WhatsApp:', error);
    return NextResponse.json(
      { success: false, message: error instanceof Error ? error.message : 'An unexpected error occurred' },
      { status: 500 }
    );
  }
} 