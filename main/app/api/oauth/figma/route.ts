import { createClient } from '@/lib/utils/supabase/server';
import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
    const supabase = await createClient();
    const { data: { user } } = await supabase.auth.getUser();
    
    if (!user) {
        return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const { scopes, return_url } = await request.json();
    
    const { data: provider } = await supabase
        .from('providers')
        .select('id')
        .eq('provider_tag', 'figma')
        .single();

    if (!provider) {
        return NextResponse.json({ error: 'Provider not found' }, { status: 404 });
    }

    const state = Buffer.from(JSON.stringify({
        provider_id: provider.id,
        scopes,
        return_url: return_url || '/integrations'
    })).toString('base64');

    const redirectUri = `${request.nextUrl.origin}/api/oauth/figma/callback`;

    const authUrl = `https://www.figma.com/oauth?` +
        `client_id=${process.env.FIGMA_CLIENT_ID}&` +
        `redirect_uri=${encodeURIComponent(redirectUri)}&` +
        `scope=${encodeURIComponent(Array.isArray(scopes) ? scopes.join(' ') : scopes)}&` +
        `state=${state}&` +
        `response_type=code`;

    return NextResponse.json({ url: authUrl });
}

export { POST as GET };