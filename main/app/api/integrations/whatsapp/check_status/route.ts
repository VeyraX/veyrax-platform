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

    // Call the WhatsApp check_status API endpoint
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/whatsapp/check_status`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${session.access_token}`
      },
      body: JSON.stringify({}),
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