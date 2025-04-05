import { createClient } from '@supabase/supabase-js';
import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();
        const { code, api_key } = body;
        
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

        const query = serviceClient
            .from('user_auth_codes')
            .select('*')
            .eq('code', code)
            .eq('used', false);
            
        if (api_key) {
            query.eq('encrypted_api_key', api_key);
        }
        
        const { data: authCode, error: authCodeError } = await query.single();

        if (authCodeError || !authCode) {
            return NextResponse.json({ 
                success: false,
                error: 'Invalid or expired authentication code or API key' 
            }, { status: 400 });
        }

        const expiresAt = new Date(authCode.expires_at);
        if (expiresAt < new Date()) {
            return NextResponse.json({ 
                success: false,
                error: 'Authentication code has expired' 
            }, { status: 400 });
        }

        const { error: updateError } = await serviceClient
            .from('user_auth_codes')
            .update({ used: true })
            .eq('code', code);

        if (updateError) {
            return NextResponse.json({ 
                success: false,
                error: 'Error validating authentication code' 
            }, { status: 500 });
        }

        return NextResponse.json({
            success: true,
            encrypted_api_key: authCode.encrypted_api_key,
            code: authCode.code
        });

    } catch (error) {
        return NextResponse.json({ 
            success: false,
            error: 'Internal server error' 
        }, { status: 500 });
    }
} 