import { createClient } from '@/lib/utils/supabase/server';
import { createClient as createServiceClient } from '@supabase/supabase-js';
import { NextRequest, NextResponse } from 'next/server';
import { encrypt } from '@/lib/utils/encryption';
import { addActionsUser, validateUserAuthentication } from '@/app/modules/integrations/api/api.integrations.server';

export async function GET(request: NextRequest) {   
    const searchParams = request.nextUrl.searchParams;
    const code = searchParams.get('code');
    const state = searchParams.get('state');
    
    if (!code || !state) {
        console.error('Missing code or state');
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
                console.error('No user found');
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
            console.error('Provider error:', providerError);
            throw new Error('Provider not found');
        }

        const tokenResponse = await fetch('https://api.vercel.com/v2/oauth/access_token', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: new URLSearchParams({
                client_id: process.env.VERCEL_CLIENT_ID!,
                client_secret: process.env.VERCEL_CLIENT_SECRET!,
                code,
                redirect_uri: `${request.nextUrl.origin}/api/oauth/vercel/callback`,
                grant_type: 'authorization_code'
            }),
        });

        const tokens = await tokenResponse.json();

        if (!tokenResponse.ok || tokens.error) {
            console.error('Token error:', tokens);
            throw new Error(tokens.error_description || tokens.error || 'Failed to obtain access token');
        }

        const accessToken = tokens.access_token;
        const refreshToken = tokens.refresh_token;
        const expiresIn = tokens.expires_in;

        if (!accessToken) {
            console.error('Missing access_token in OAuth response:', tokens);
            throw new Error('OAuth failed: Missing access token');
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
            console.error('Provider upsert error:', providerUpsertError);
            throw providerUpsertError;
        }

        const encryptedAccessToken = encrypt(accessToken);
        const encryptedRefreshToken = refreshToken ? encrypt(refreshToken) : null;
        
        const encryptedTokenData = {
            ...tokens,
            access_token: encryptedAccessToken,
            refresh_token: encryptedRefreshToken
        };
        
        const { error: upsertError } = await client
            .from('users_oauth_tokens')
            .upsert({
                user_id: user_id,
                provider_id: provider_id,
                access_token: encryptedAccessToken,
                refresh_token: encryptedRefreshToken,
                expires_at: expiresIn 
                    ? Math.floor(Date.now() / 1000) + expiresIn 
                    : null,
                scopes: Array.isArray(scopes) ? scopes.join(',') : scopes,
                raw_token_data: encryptedTokenData,
            }, {
                onConflict: 'user_id,provider_id'
            });

        if (upsertError) {
            console.error('Upsert error:', upsertError);
            throw upsertError;
        }

        await addActionsUser(provider_id, user_id);

        return NextResponse.redirect(`${request.nextUrl.origin}${return_url}?success=true`);
    } catch (error: any) {
        console.error('OAuth callback error:', {
            message: error.message,
            error: error
        });
        return NextResponse.redirect(
            `${request.nextUrl.origin}/integrations?error=${encodeURIComponent(error.message || 'Unknown error')}`
        );
    }
}
