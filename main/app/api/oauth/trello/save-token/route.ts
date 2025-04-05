import { createClient } from '@/lib/utils/supabase/server';
import { createClient as createServiceClient } from '@supabase/supabase-js';
import { NextRequest, NextResponse } from 'next/server';
import { encrypt } from '@/lib/utils/encryption';
import { addActionsUser, validateUserAuthentication } from '@/app/modules/integrations/api/api.integrations.server';


export async function POST(request: NextRequest) {
    try {
        const { token, state } = await request.json();
        
        if (!token) {
            console.error('Missing token');
            return NextResponse.json({ error: 'Missing token' }, { status: 400 });
        }

        let user_id;
        let client;
        
        if (state) {
            try {
                const decodedState = JSON.parse(Buffer.from(state, 'base64').toString());
                const { user_id: stateUserId, encrypted_api_key, code: stateCode, return_url } = decodedState;
                
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
                        return NextResponse.json({ error: 'Authentication failed' }, { status: 401 });
                    }
                } else if (stateUserId) {
                    user_id = stateUserId;
                    client = createServiceClient(
                        process.env.NEXT_PUBLIC_SUPABASE_URL!,
                        process.env.SUPABASE_SERVICE_KEY!
                    );
                }
            } catch (stateError) {
                console.error('Error decoding state:', stateError);
            }
        }
        
        if (!client) {
            const supabase = await createClient();
            const { data: { user } } = await supabase.auth.getUser();
            
            if (!user) {
                console.error('Unauthorized: No user found');
                return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
            }
            
            user_id = user.id;
            client = supabase;
        }

        const { data: provider, error: providerError } = await client
            .from('providers')
            .select('*')
            .eq('provider_tag', 'trello')
            .single();

        if (providerError || !provider) {
            console.error('Provider error:', providerError);
            return NextResponse.json({ error: 'Trello provider not found' }, { status: 404 });
        }

        const provider_id = provider.id;

        const verifyResponse = await fetch(`https://api.trello.com/1/members/me?key=${process.env.TRELLO_API_KEY}&token=${token}`);
        
        if (!verifyResponse.ok) {
            const errorText = await verifyResponse.text();
            console.error('Token verification failed:', {
                status: verifyResponse.status,
                statusText: verifyResponse.statusText,
                errorText
            });
            return NextResponse.json({ error: 'Invalid Trello token' }, { status: 400 });
        }
        
        const userData = await verifyResponse.json();


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
            return NextResponse.json({ error: 'Failed to save provider connection' }, { status: 500 });
        }

        const encryptedAccessToken = encrypt(token);
        const tenYearsInSeconds = 10 * 365 * 24 * 60 * 60;
        
        const encryptedTokenData = {
            access_token: encryptedAccessToken
        };
        
        const { error: upsertError } = await client
            .from('users_oauth_tokens')
            .upsert({
                user_id: user_id,
                provider_id: provider_id,
                access_token: encryptedAccessToken,
                refresh_token: null,
                expires_at: Math.floor(Date.now() / 1000) + tenYearsInSeconds,
                scopes: 'read,write',
                raw_token_data: encryptedTokenData,
            }, {
                onConflict: 'user_id,provider_id'
            });

        if (upsertError) {
            console.error('Upsert error:', upsertError);
            return NextResponse.json({ error: 'Failed to save token' }, { status: 500 });
        }

        await addActionsUser(provider_id, user_id);

        return NextResponse.json({ success: true });
    } catch (error: any) {
        console.error('Save token error:', error);
        return NextResponse.json({ 
            error: error.message || 'Unknown error' 
        }, { status: 500 });
    }
}