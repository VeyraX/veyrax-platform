import { createClient } from '@/lib/utils/supabase/server';
import { NextRequest, NextResponse } from 'next/server';
import { encrypt } from '@/lib/utils/encryption';

export async function GET(request: NextRequest) {
    const searchParams = request.nextUrl.searchParams;
    const code = searchParams.get('code');
    const state = searchParams.get('state');
    
    console.log('Callback received - code exists:', !!code);
    console.log('Callback received - state exists:', !!state);
    
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
        // Decode the state parameter to get the code_verifier
        const decodedState = Buffer.from(state, 'base64').toString();
        console.log('Decoded state:', decodedState);
        const { provider_id, scopes, code_verifier } = JSON.parse(decodedState);
        
        console.log('Code verifier exists:', !!code_verifier);
        console.log('Code verifier length:', code_verifier?.length);

        if (!code_verifier) {
            console.error('Missing code_verifier in state');
            throw new Error('Invalid authorization state - missing code verifier');
        }

        const { data: provider, error: providerError } = await supabase
            .from('providers')
            .select('*')
            .eq('id', provider_id)
            .single();

        if (providerError || !provider) {
            console.error('Provider error:', providerError);
            throw new Error('Provider not found');
        }

        const redirectUri = `${request.nextUrl.origin}/api/oauth/airtable/callback`;
        
        // Create the token request with the code_verifier for PKCE
        const tokenRequestBody = new URLSearchParams();
        tokenRequestBody.append('grant_type', 'authorization_code');
        tokenRequestBody.append('code', code);
        tokenRequestBody.append('redirect_uri', redirectUri);
        tokenRequestBody.append('code_verifier', code_verifier); // This is essential for PKCE
        tokenRequestBody.append('client_id', process.env.AIRTABLE_CLIENT_ID || '');
        tokenRequestBody.append('client_secret', process.env.AIRTABLE_CLIENT_SECRET || '');

        console.log('Token request - client_id:', process.env.AIRTABLE_CLIENT_ID);
        console.log('Token request - client_secret length:', process.env.AIRTABLE_CLIENT_SECRET?.length);
        console.log('Token request - redirect_uri:', redirectUri);
        console.log('Token request - code_verifier (first 10 chars):', code_verifier?.substring(0, 10) + '...');
        
        const tokenResponse = await fetch('https://airtable.com/oauth2/v1/token', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: tokenRequestBody.toString(),
        });

        const responseText = await tokenResponse.text();
        
        try {
            const tokens = JSON.parse(responseText);
            
            if (tokens.error) {
                console.error('Token error:', tokens);
                
                if (tokens.error === 'invalid_client') {
                    console.error('Client credentials issue - check your Airtable app configuration');
                    return NextResponse.redirect(
                        `${request.nextUrl.origin}/integrations?error=${encodeURIComponent('Invalid Airtable client credentials - verify your app credentials in Airtable')}`
                    );
                }
                
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

            const expiresIn = tokens.expires_in || 31536000; // 1 year if not specified

            const { error: upsertError } = await supabase
                .from('users_oauth_tokens')
                .upsert({
                    user_id: user.id,
                    provider_id: provider_id,
                    access_token: encryptedAccessToken,
                    refresh_token: encryptedRefreshToken,
                    expires_at: Math.floor(Date.now() / 1000) + expiresIn,
                    scopes: Array.isArray(scopes) ? scopes.join(',') : scopes,
                    raw_token_data: encryptedTokenData,
                }, {
                    onConflict: 'user_id,provider_id'
                });

            if (upsertError) {
                console.error('Upsert error:', upsertError);
                throw upsertError;
            }

            return NextResponse.redirect(`${request.nextUrl.origin}/integrations?success=true`);
        } catch (parseError) {
            console.error('Failed to parse token response:', parseError);
            console.error('Raw response:', responseText);
            throw new Error(`Invalid response from token endpoint: ${responseText}`);
        }
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
