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

    // Call the WhatsApp disconnect API endpoint
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/whatsapp/disconnect`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${session.access_token}`
      },
      // Empty body since DisconnectRequest doesn't require any parameters
      body: JSON.stringify({}),
    });

    if (!response.ok) {
      const errorText = await response.text();
      return NextResponse.json(
        { success: false, message: `WhatsApp disconnect failed: ${errorText}` },
        { status: response.status }
      );
    }

    const data = await response.json();

    console.log("[WhatsApp disconnect] data", data);
    
    // Return the response data
    return NextResponse.json({
      success: true,
      data: {
        success: data.data?.success,
        message: data.data?.message,
      },
      message: 'WhatsApp disconnected successfully'
    });
  } catch (error) {
    console.error('Error disconnecting WhatsApp:', error);
    return NextResponse.json(
      { success: false, message: error instanceof Error ? error.message : 'An unexpected error occurred' },
      { status: 500 }
    );
  }
} 