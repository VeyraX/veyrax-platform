import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@/lib/utils/supabase/server';

export async function POST(request: NextRequest) {
  try {
    const supabase = createClient();
    const { data: { session } } = await supabase.auth.getSession();

    if (!session) {
      return NextResponse.json(
        { success: false, message: 'Authentication required' },
        { status: 401 }
      );
    }

    const userId = session.user.id;

    // Call the WhatsApp authenticate API endpoint
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/whatsapp/authenticate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${session.access_token}`
      },
      body: JSON.stringify({
            "include_component": false,
            "include_qr_ascii": false
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      return NextResponse.json(
        { success: false, message: `WhatsApp authentication failed: ${errorText}` },
        { status: response.status }
      );
    }

    const data = await response.json();

    console.log("[WhatsApp authenticate] data", data);
    
    // Process the response and extract relevant information
    // The response should include QR code data or authentication status
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