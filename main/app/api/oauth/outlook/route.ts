import { createClient } from '@/lib/utils/supabase/server';
import { createClient as createServiceClient } from '@supabase/supabase-js';
import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
    const { scopes, return_url, encrypted_api_key, code } = await request.json();
    
    let supabase;
    let user_id;
    
    if (encrypted_api_key) {
        supabase = createServiceClient(
            process.env.NEXT_PUBLIC_SUPABASE_URL!,
            process.env.SUPABASE_SERVICE_KEY!
        );
    } else {
        supabase = await createClient();
        const { data: { user } } = await supabase.auth.getUser();
        
        if (!user) {
            return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
        }
        user_id = user.id;
    }
    
    const { data: provider } = await supabase
        .from('providers')
        .select('id')
        .eq('provider_tag', 'outlook')
        .single();

    if (!provider) {
        return NextResponse.json({ error: 'Provider not found' }, { status: 404 });
    }

    const state = Buffer.from(JSON.stringify({
        provider_id: provider.id,
        scopes,
        return_url: return_url || '/integrations',
        user_id,
        encrypted_api_key,
        code
    })).toString('base64');

    const redirectUri = `${request.nextUrl.origin}/api/oauth/outlook/callback`;

    const scopesWithOffline = [...scopes, 'offline_access'];

    const authUrl = `https://login.microsoftonline.com/common/oauth2/v2.0/authorize?` +
        `client_id=${process.env.OUTLOOK_CLIENT_ID}&` +
        `response_type=code&` +
        `redirect_uri=${encodeURIComponent(redirectUri)}&` +
        `scope=${encodeURIComponent(scopesWithOffline.join(' '))}&` +
        `response_mode=query&` +
        `state=${state}`;

    return NextResponse.json({ url: authUrl });
}

export { POST as GET };