import { createClient } from '@/lib/utils/supabase/server';
import { NextRequest, NextResponse } from 'next/server';
import { encrypt } from '@/lib/utils/encryption';
import { addActionsUser } from '@/app/modules/integrations/api/api.integrations.server';

export async function GET(request: NextRequest) {
    const searchParams = request.nextUrl.searchParams;
    const code = searchParams.get('code');
    const state = searchParams.get('state');
    
    if (!code || !state) {
        return NextResponse.redirect(`${request.nextUrl.origin}/integrations?error=Invalid request`);
    }

    const supabase = await createClient();
    const { data: { user } } = await supabase.auth.getUser();
    
    if (!user) {
        return NextResponse.redirect(`${request.nextUrl.origin}/integrations?error=Unauthorized`);
    }

    try {
        const decodedState = Buffer.from(state, 'base64').toString();
        const { provider_id, scopes, code_verifier } = JSON.parse(decodedState);

        const { data: provider, error: providerError } = await supabase
            .from('providers')
            .select('*')
            .eq('id', provider_id)
            .single();

        if (providerError || !provider) {
            throw new Error('Provider not found');
        }

        const redirectUri = `${request.nextUrl.origin}/api/oauth/airtable/callback`;
        
        const clientId = process.env.AIRTABLE_CLIENT_ID;
        const clientSecret = process.env.AIRTABLE_CLIENT_SECRET;
        const basicAuth = Buffer.from(`${clientId}:${clientSecret}`).toString('base64');
        
        const formData = new URLSearchParams();
        formData.append('grant_type', 'authorization_code');
        formData.append('code', code);
        formData.append('redirect_uri', redirectUri);
        formData.append('code_verifier', code_verifier);
        
        try {
            
            const response = await fetch('https://airtable.com/oauth2/v1/token', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Authorization': `Basic ${basicAuth}`
                },
                body: formData.toString(),
            });
            
            const responseText = await response.text();
            
            if (!response.ok) {
                
                if (responseText.includes('invalid_client')) {
                    return NextResponse.redirect(
                        `${request.nextUrl.origin}/integrations?error=${encodeURIComponent('Your Airtable app credentials appear to be invalid. Please verify your app registration in the Airtable developer portal.')}`
                    );
                }
                
                throw new Error(`Token request failed: ${response.status} ${response.statusText} - ${responseText}`);
            }
            
            const tokens = JSON.parse(responseText);
            return await processTokens(tokens, user.id, provider_id, scopes, request);
            
        } catch (error) {
            throw error;
        }
    } catch (error: any) {
        return NextResponse.redirect(
            `${request.nextUrl.origin}/integrations?error=${encodeURIComponent(error.message || 'Unknown error')}`
        );
    }
}

async function processTokens(tokens: any, userId: string, providerId: string, scopes: string[], request: NextRequest) {
    const supabase = await createClient();
    
    const { error: providerUpsertError } = await supabase
        .from('users_providers')
        .upsert({
            user_id: userId,
            provider_id: providerId
        }, {
            onConflict: 'user_id,provider_id'
        });

    if (providerUpsertError) {
        throw providerUpsertError;
    }

    const encryptedAccessToken = encrypt(tokens.access_token);
    const encryptedRefreshToken = tokens.refresh_token ? encrypt(tokens.refresh_token) : null;
    
    const encryptedTokenData = {
        ...tokens,
        access_token: encryptedAccessToken,
        refresh_token: encryptedRefreshToken
    };

    const expiresIn = tokens.expires_in || 31536000;

    const { error: upsertError } = await supabase
        .from('users_oauth_tokens')
        .upsert({
            user_id: userId,
            provider_id: providerId,
            access_token: encryptedAccessToken,
            refresh_token: encryptedRefreshToken,
            expires_at: Math.floor(Date.now() / 1000) + expiresIn,
            scopes: Array.isArray(scopes) ? scopes.join(',') : scopes,
            raw_token_data: encryptedTokenData,
        }, {
            onConflict: 'user_id,provider_id'
        });

    if (upsertError) {
        throw upsertError;
    }
    
    await addActionsUser(providerId);

    return NextResponse.redirect(`${request.nextUrl.origin}/integrations?success=true`);
}
