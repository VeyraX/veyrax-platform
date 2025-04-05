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
        .eq('provider_tag', 'todoist')
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

    const redirectUri = `${request.nextUrl.origin}/api/oauth/todoist/callback`;

    const authUrl = `https://todoist.com/oauth/authorize?` +
        `client_id=${process.env.TODOIST_CLIENT_ID}&` +
        `scope=${encodeURIComponent(scopes.join(','))}&` +
        `state=${state}&` +
        `redirect_uri=${encodeURIComponent(redirectUri)}`;

    return NextResponse.json({ url: authUrl });
}

export { POST as GET };
