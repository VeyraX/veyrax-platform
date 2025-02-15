import { createClient } from '@/lib/utils/supabase/server';
import { NextRequest, NextResponse } from 'next/server';

export const SCOPES = [
    'read_databases',
    'write_databases',
    'read_pages',
    'write_pages'
].join(' ');

export async function GET(request: NextRequest) {
    const supabase = await createClient();
    const { data: { user } } = await supabase.auth.getUser();
    
    if (!user) {
        return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const { data: provider } = await supabase
        .from('providers')
        .select('id')
        .eq('provider_tag', 'notion')
        .single();

    if (!provider) {
        return NextResponse.json({ error: 'Provider not found' }, { status: 404 });
    }

    const state = Buffer.from(JSON.stringify({
        provider_id: provider.id
    })).toString('base64');

    const redirectUri = `${request.nextUrl.origin}/api/oauth/notion/callback`;

    const authUrl = `https://api.notion.com/v1/oauth/authorize?` +
        `client_id=${process.env.NOTION_CLIENT_ID}&` +
        `response_type=code&` +
        `owner=user&` +
        `redirect_uri=${encodeURIComponent(redirectUri)}&` +
        `state=${state}`;

    return NextResponse.json({ url: authUrl });
}