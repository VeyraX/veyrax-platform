import { createClient } from '@/lib/utils/supabase/server';
import { createClient as createServiceClient } from '@supabase/supabase-js';
import { NextRequest, NextResponse } from 'next/server';

type TickTickScope = 'tasks:write' | 'tasks:read';

export async function POST(request: NextRequest) {
    if (!process.env.TICK_TICK_CLIENT_ID || !process.env.TICK_TICK_CLIENT_SECRET) {
        console.error('[TickTick OAuth] Missing client credentials');
        return NextResponse.json({ error: 'Configuration error' }, { status: 500 });
    }

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
    
    const validScopes: TickTickScope[] = ['tasks:write', 'tasks:read'];
    const uniqueScopes = Array.from(new Set<string>(scopes))
        .filter((scope): scope is TickTickScope => validScopes.includes(scope as TickTickScope));
    
    const { data: provider } = await supabase
        .from('providers')
        .select('id')
        .eq('provider_tag', 'ticktick')
        .single();

    const state = Buffer.from(JSON.stringify({
        provider_id: provider?.id,
        scopes: uniqueScopes,
        return_url: return_url || '/integrations',
        user_id,
        encrypted_api_key,
        code
    })).toString('base64');

    const redirectUri = `${request.nextUrl.origin}/api/oauth/ticktick/callback`;

    const authUrl = `https://ticktick.com/oauth/authorize?` +
        `client_id=${process.env.TICK_TICK_CLIENT_ID}&` +
        `redirect_uri=${encodeURIComponent(redirectUri)}&` +
        `response_type=code&` +
        `scope=${encodeURIComponent(uniqueScopes.join(' '))}&` +
        `state=${state}`;

    return NextResponse.json({ url: authUrl });
}


export { POST as GET }; 