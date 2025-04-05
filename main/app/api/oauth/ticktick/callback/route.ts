import { createClient } from '@/lib/utils/supabase/server';
import { createClient as createServiceClient } from '@supabase/supabase-js';
import { NextRequest, NextResponse } from 'next/server';
import { encrypt } from '@/lib/utils/encryption';
import { addActionsUser, validateUserAuthentication } from '@/app/modules/integrations/api/api.integrations.server';


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

    try {
        const decodedState = Buffer.from(state, 'base64').toString();
        const { provider_id, scopes, return_url, user_id: stateUserId, encrypted_api_key, code: stateCode } = JSON.parse(decodedState);

        let user_id;
        let client;
        
        if (encrypted_api_key) {
            try {
                user_id = await validateUserAuthentication({
                    encrypted_api_key,
                    code: stateCode
                });
                
                client = createServiceClient(
                    process.env.NEXT_PUBLIC_SUPABASE_URL!,
                    process.env.SUPABASE_SERVICE_KEY!
                );
            } catch (authError) {
                console.error('Auth error with API key:', authError);
                return NextResponse.redirect(`${request.nextUrl.origin}/integrations?error=Authentication failed`);
            }
        } else if (stateUserId) {
            user_id = stateUserId;
            client = createServiceClient(
                process.env.NEXT_PUBLIC_SUPABASE_URL!,
                process.env.SUPABASE_SERVICE_KEY!
            );
        } else {
            const supabase = await createClient();
            const { data: { user } } = await supabase.auth.getUser();
            
            if (!user) {
                console.error('[TickTick Callback] No user found');
                return NextResponse.redirect(`${request.nextUrl.origin}/integrations?error=Unauthorized`);
            }
            user_id = user.id;
            client = supabase;
        }

        const { data: provider, error: providerError } = await client
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

        const { error: providerUpsertError } = await client
            .from('users_providers')
            .upsert({
                user_id: user_id,
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

        const { error: upsertError } = await client
            .from('users_oauth_tokens')
            .upsert({
                user_id: user_id,
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

        await addActionsUser(provider_id, user_id);

        return NextResponse.redirect(`${request.nextUrl.origin}${return_url}?success=true`);
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