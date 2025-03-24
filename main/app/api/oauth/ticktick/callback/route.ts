import { createClient } from '@/lib/utils/supabase/server';
import { NextRequest, NextResponse } from 'next/server';
import { encrypt } from '@/lib/utils/encryption';
import { addActionsUser } from '@/app/modules/integrations/api/api.integrations';


export async function GET(request: NextRequest) {
    if (!process.env.TICK_TICK_CLIENT_ID || !process.env.TICK_TICK_CLIENT_SECRET) {
        console.error('[TickTick Callback] Missing TickTick credentials in environment');
        return NextResponse.redirect(`${request.nextUrl.origin}/integrations?error=Configuration error`);
    }

    const searchParams = request.nextUrl.searchParams;
    const code = searchParams.get('code');
    const state = searchParams.get('state');
    
    if (!code || !state) {
        console.error('[TickTick Callback] Missing code or state');
        return NextResponse.redirect(`${request.nextUrl.origin}/integrations?error=Invalid request`);
    }

    const supabase = await createClient();
    const { data: { user } } = await supabase.auth.getUser();
    
    if (!user) {
        console.error('[TickTick Callback] No user found');
        return NextResponse.redirect(`${request.nextUrl.origin}/integrations?error=Unauthorized`);
    }

    try {
        const decodedState = Buffer.from(state, 'base64').toString();
        const { provider_id, scopes } = JSON.parse(decodedState);

        const { data: provider, error: providerError } = await supabase
            .from('providers')
            .select('*')
            .eq('id', provider_id)
            .single();

        if (providerError || !provider) {
            console.error('[TickTick Callback] Provider error:', providerError);
            throw new Error('Provider not found');
        }

        const redirectUri = `${request.nextUrl.origin}/api/oauth/ticktick/callback`;
        
        const bodyParams = new URLSearchParams({
            client_id: process.env.TICK_TICK_CLIENT_ID,
            client_secret: process.env.TICK_TICK_CLIENT_SECRET,
            code,
            grant_type: 'authorization_code',
            redirect_uri: redirectUri,
            scope: Array.isArray(scopes) ? scopes.join(' ') : scopes,
        });

        const tokenResponse = await fetch('https://ticktick.com/oauth/token', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: bodyParams.toString(),
        });
        
        if (!tokenResponse.ok) {
            const errorText = await tokenResponse.text();
            console.error('[TickTick Callback] Token request failed:', errorText);
            throw new Error(`TickTick OAuth token request failed (${tokenResponse.status})`);
        }

        const tokens = await tokenResponse.json();

        if (tokens.error) {
            console.error('[TickTick Callback] Token error:', tokens);
            throw new Error(tokens.error_description || tokens.error);
        }

        const { error: providerUpsertError } = await supabase
            .from('users_providers')
            .upsert({
                user_id: user.id,
                provider_id: provider_id
            }, {
                onConflict: 'user_id,provider_id'
            });

        if (providerUpsertError) {
            console.error('[TickTick Callback] Provider upsert error:', providerUpsertError);
            throw providerUpsertError;
        }

        const encryptedAccessToken = encrypt(tokens.access_token);
        
        const encryptedTokenData = {
            ...tokens,
            access_token: encryptedAccessToken
        };

        const { error: upsertError } = await supabase
            .from('users_oauth_tokens')
            .upsert({
                user_id: user.id,
                provider_id: provider_id,
                access_token: encryptedAccessToken,
                refresh_token: null,
                expires_at: Math.floor(Date.now() / 1000) + tokens.expires_in,
                scopes: Array.isArray(scopes) ? scopes.join(',') : scopes,
                raw_token_data: encryptedTokenData,
            }, {
                onConflict: 'user_id,provider_id'
            });

        if (upsertError) {
            console.error('[TickTick Callback] Upsert error:', upsertError);
            throw upsertError;
        }

        await addActionsUser(provider_id);

        return NextResponse.redirect(`${request.nextUrl.origin}/integrations?success=true`);
    } catch (error: any) {
        console.error('[TickTick Callback] Error:', {
            message: error.message,
            error: error
        });
        return NextResponse.redirect(
            `${request.nextUrl.origin}/integrations?error=${encodeURIComponent(error.message || 'Unknown error')}`
        );
    }
} 