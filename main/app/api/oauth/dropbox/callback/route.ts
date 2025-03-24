import { createClient } from '@/lib/utils/supabase/server';
import { NextRequest, NextResponse } from 'next/server';
import { encrypt } from '@/lib/utils/encryption';
import { addActionsUser } from '@/app/modules/integrations/api/api.integrations';


export async function GET(request: NextRequest) {
    const searchParams = request.nextUrl.searchParams;
    const code = searchParams.get('code');
    const state = searchParams.get('state');
    
    if (!code || !state) {
        console.error('Missing code or state');
        return NextResponse.redirect(`${request.nextUrl.origin}/integrations?error=Invalid request`);
    }

    const supabase = await createClient();
    const { data: { user } } = await supabase.auth.getUser();
    
    if (!user) {
        console.error('No user found');
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
            console.error('Provider error:', providerError);
            throw new Error('Provider not found');
        }

        const redirectUri = `${request.nextUrl.origin}/api/oauth/dropbox/callback`;
        
        const tokenResponse = await fetch('https://api.dropboxapi.com/oauth2/token', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/x-www-form-urlencoded' 
            },
            body: new URLSearchParams({
                grant_type: 'authorization_code',
                client_id: process.env.DROPBOX_CLIENT_ID!,
                client_secret: process.env.DROPBOX_CLIENT_SECRET!,
                code,
                redirect_uri: redirectUri
            }).toString(),
        });

        const tokens = await tokenResponse.json();

        if (tokens.error) {
            console.error('Token error:', tokens);
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
            console.error('Provider upsert error:', providerUpsertError);
            throw providerUpsertError;
        }

        const encryptedAccessToken = encrypt(tokens.access_token);
        const encryptedRefreshToken = tokens.refresh_token ? encrypt(tokens.refresh_token) : null;
        
        const encryptedTokenData = {
            ...tokens,
            access_token: encryptedAccessToken,
            refresh_token: encryptedRefreshToken
        };

        const { error: upsertError } = await supabase
            .from('users_oauth_tokens')
            .upsert({
                user_id: user.id,
                provider_id: provider_id,
                access_token: encryptedAccessToken,
                refresh_token: encryptedRefreshToken,
                expires_at: Math.floor(Date.now() / 1000) + tokens.expires_in,
                scopes: Array.isArray(scopes) ? scopes.join(',') : scopes,
                raw_token_data: encryptedTokenData,
            }, {
                onConflict: 'user_id,provider_id'
            });

        if (upsertError) {
            console.error('Upsert error:', upsertError);
            throw upsertError;
        }

        await addActionsUser(provider_id);

        return NextResponse.redirect(`${request.nextUrl.origin}/integrations?success=true`);
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