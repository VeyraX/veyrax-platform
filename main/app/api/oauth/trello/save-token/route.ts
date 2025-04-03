import { createClient } from '@/lib/utils/supabase/server';
import { NextRequest, NextResponse } from 'next/server';
import { encrypt } from '@/lib/utils/encryption';
import { addActionsUser } from '@/app/modules/integrations/api/api.integrations.server';


export async function POST(request: NextRequest) {
    const supabase = await createClient();
    const { data: { user } } = await supabase.auth.getUser();
    
    if (!user) {
        console.error('Unauthorized: No user found');
        return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    try {
        const { token } = await request.json();
        
        
        if (!token) {
            console.error('Missing token');
            return NextResponse.json({ error: 'Missing token' }, { status: 400 });
        }

        // Получаем provider_id для Trello
        const { data: provider, error: providerError } = await supabase
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
            return NextResponse.json({ error: 'Failed to save provider connection' }, { status: 500 });
        }

        const encryptedAccessToken = encrypt(token);
        const tenYearsInSeconds = 10 * 365 * 24 * 60 * 60;
        
        const { error: upsertError } = await supabase
            .from('users_oauth_tokens')
            .upsert({
                user_id: user.id,
                provider_id: provider_id,
                access_token: encryptedAccessToken,
                refresh_token: null,
                expires_at: Math.floor(Date.now() / 1000) + tenYearsInSeconds,
                scopes: 'read,write',
                raw_token_data: { access_token: encryptedAccessToken },
            }, {
                onConflict: 'user_id,provider_id'
            });

        if (upsertError) {
            console.error('Upsert error:', upsertError);
            return NextResponse.json({ error: 'Failed to save token' }, { status: 500 });
        }

        await addActionsUser(provider_id);

        return NextResponse.json({ success: true });
    } catch (error: any) {
        console.error('Save token error:', error);
        return NextResponse.json({ 
            error: error.message || 'Unknown error' 
        }, { status: 500 });
    }
}