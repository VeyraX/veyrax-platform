import { createClient } from '@/lib/utils/supabase/server';
import { NextRequest, NextResponse } from 'next/server';
import { encrypt } from '@/lib/utils/encryption';
import { addActionsUser } from '@/app/modules/integrations/api/api.integrations.server';


export async function GET(request: NextRequest) {
    const searchParams = request.nextUrl.searchParams;
    const code = searchParams.get('code');
    const state = searchParams.get('state');
    const installationId = searchParams.get('installationId');
    const orgSlug = searchParams.get('orgSlug');
    
    // For public integrations, we must have both code, state and installationId
    if (!code || !state || !installationId) {
        console.error('Missing required parameters:', { 
            code: code ? 'present' : 'missing', 
            state: state ? 'present' : 'missing',
            installationId: installationId ? 'present' : 'missing'
        });
        return NextResponse.redirect(`${request.nextUrl.origin}/integrations?error=Invalid request - missing parameters`);
    }

    // Log the received parameters for debugging
    console.log('Sentry callback received:', { 
        code: 'present', 
        state: 'present',
        searchParams
    });

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

        // For public integrations, we must use the installation ID endpoint
        const tokenUrl = `https://sentry.io/api/0/sentry-app-installations/${installationId}/authorizations/`;

        const tokenPayload = {
            grant_type: 'authorization_code',
            code,
            client_id: process.env.SENTRY_INTEGRATION_CLIENT_ID,
            client_secret: process.env.SENTRY_INTEGRATION_CLIENT_SECRET,
        };
        
        // Exchange the authorization code for an access token
        const tokenResponse = await fetch(tokenUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(tokenPayload),
        });

        if (!tokenResponse.ok) {
            const errorData = await tokenResponse.json();
            console.error('Token exchange failed:', errorData);
            throw new Error(`Token exchange failed: ${JSON.stringify(errorData)}`);
        }

        const tokens = await tokenResponse.json();

        // For public integrations, the token field names are different from standard OAuth
        const accessToken = tokens.token;
        const refreshToken = tokens.refreshToken;
        
        if (!accessToken) {
            console.error('No access token in response:', tokens);
            throw new Error('Failed to obtain access token');
        }
        
        // Calculate expiration time - Sentry tokens expire after 8 hours (28800 seconds)
        // Use the expiresAt from the response if available
        const expiresAt = tokens.expiresAt 
            ? Math.floor(new Date(tokens.expiresAt).getTime() / 1000)
            : Math.floor(Date.now() / 1000) + 28800;

        // Store the user-provider relationship
        const { error: providerUpsertError } = await supabase
            .from('users_providers')
            .upsert({
                user_id: user.id,
                provider_id: provider_id
            }, {
                onConflict: 'user_id,provider_id'
            });

        if (providerUpsertError) {
            throw providerUpsertError;
        }

        // Encrypt the tokens before storing them
        const encryptedAccessToken = encrypt(accessToken);
        const encryptedRefreshToken = refreshToken ? encrypt(refreshToken) : null;
        
        // Store the installation ID
        const additionalData = { installation_id: installationId, org_slug: orgSlug };
        
        const encryptedTokenData = {
            ...tokens,
            access_token: encryptedAccessToken,
            refresh_token: encryptedRefreshToken,
            ...additionalData
        };

        // Store the OAuth tokens
        const { error: upsertError } = await supabase
            .from('users_oauth_tokens')
            .upsert({
                user_id: user.id,
                provider_id: provider_id,
                access_token: encryptedAccessToken,
                refresh_token: encryptedRefreshToken,
                expires_at: expiresAt,
                scopes: Array.isArray(scopes) ? scopes.join(',') : scopes,
                raw_token_data: encryptedTokenData
            }, {
                onConflict: 'user_id,provider_id'
            });

        if (upsertError) {
            throw upsertError;
        }

        // Mark the installation as officially installed
        try {
            console.log('Verifying installation:', installationId);
            const verifyResponse = await fetch(`https://sentry.io/api/0/sentry-app-installations/${installationId}/`, {
                method: 'PUT',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${accessToken}`
                },
                body: JSON.stringify({ status: 'installed' }),
            });
            
            if (!verifyResponse.ok) {
                const verifyError = await verifyResponse.json();
                console.error('Installation verification failed:', verifyError);
            } else {
                console.log('Installation verified successfully');
            }
        } catch (verifyError) {
            console.error('Failed to verify installation:', verifyError);
            // Continue even if verification fails
        }

        await addActionsUser(provider_id);

        // Redirect back to the integrations page with success message
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