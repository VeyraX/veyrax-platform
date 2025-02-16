import { createClient } from '@/lib/utils/supabase/server';
import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
    const supabase = await createClient();
    const { data: { user } } = await supabase.auth.getUser();
    
    if (!user) {
        return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const { scopes } = await request.json();
    
    const { data: provider } = await supabase
        .from('providers')
        .select('id')
        .eq('provider_tag', 'google-calendar')
        .single();

    if (!provider) {
        return NextResponse.json({ error: 'Provider not found' }, { status: 404 });
    }

    const state = Buffer.from(JSON.stringify({
        provider_id: provider.id,
        scopes
    })).toString('base64');

    const redirectUri = `${request.nextUrl.origin}/api/oauth/google-calendar/callback`;

    const authUrl = `https://accounts.google.com/o/oauth2/v2/auth?` +
        `client_id=${process.env.GOOGLE_CLIENT_ID}&` +
        `response_type=code&` +
        `redirect_uri=${encodeURIComponent(redirectUri)}&` +
        `scope=${encodeURIComponent(scopes.join(' '))}&` +
        `access_type=offline&` +
        `prompt=consent&` +
        `state=${state}`;

    return NextResponse.json({ url: authUrl });
}

export { POST as GET };