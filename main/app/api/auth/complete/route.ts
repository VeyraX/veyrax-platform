import { createClient } from '@supabase/supabase-js';
import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();
        const { code } = body;
        
        if (!code) {
            return NextResponse.json({ 
                success: false,
                error: 'Authentication code is required' 
            }, { status: 400 });
        }

        const serviceClient = createClient(
            process.env.SUPABASE_URL!,
            process.env.SUPABASE_SERVICE_KEY!
        );

        const { data: authCode, error: authCodeError } = await serviceClient
            .from('user_auth_codes')
            .select('*')
            .eq('code', code)
            .eq('used', false)
            .single();

        if (authCodeError || !authCode) {
            return NextResponse.json({ 
                success: false,
                error: 'Invalid or expired authentication code' 
            }, { status: 400 });
        }

        const { error: updateError } = await serviceClient
            .from('user_auth_codes')
            .update({ used: true })
            .eq('code', code);

        if (updateError) {
            return NextResponse.json({ 
                success: false,
                error: 'Error completing authentication process' 
            }, { status: 500 });
        }

        return NextResponse.json({
            success: true,
            message: 'Authentication process completed successfully'
        });

    } catch (error) {
        return NextResponse.json({ 
            success: false,
            error: 'Internal server error' 
        }, { status: 500 });
    }
} 