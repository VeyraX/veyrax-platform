import { createClient } from '@/lib/utils/supabase/server';
import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
    const supabase = await createClient();
    const { data: { user } } = await supabase.auth.getUser();
    
    if (!user) {
        return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const { scopes = [] } = await request.json();
    
    const { data: provider } = await supabase
        .from('providers')
        .select('id')
        .eq('provider_tag', 'airtable')
        .single();

    if (!provider) {
        return NextResponse.json({ error: 'Provider not found' }, { status: 404 });
    }

    const state = Buffer.from(JSON.stringify({
        provider_id: provider.id,
        scopes
    })).toString('base64');

    const redirectUri = `${request.nextUrl.origin}/api/oauth/airtable/callback`;

    const scopeString = Array.isArray(scopes) && scopes.length > 0 
        ? scopes.join(' ') 
        : 'data.records:read data.records:write schema.bases:read';

    const authUrl = `https://airtable.com/oauth2/v1/authorize?` +
        `client_id=${process.env.AIRTABLE_CLIENT_ID}&` +
        `response_type=code&` +
        `redirect_uri=${encodeURIComponent(redirectUri)}&` +
        `state=${state}&` +
        `scope=${encodeURIComponent(scopeString)}`;

    return NextResponse.json({ url: authUrl });
}

export { POST as GET };
