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
        .select('id, provider_tag')
        .eq('provider_tag', 'trello')
        .single();

    if (!provider) {
        return NextResponse.json({ error: 'Provider not found' }, { status: 404 });
    }

    const returnUrl = `${request.nextUrl.origin}/integrations/${provider.provider_tag }/auth-complete`;
    
    const authUrl = `https://trello.com/1/authorize?` +
        `expiration=never&` +
        `name=Veyrax&` +
        `scope=${encodeURIComponent(Array.isArray(scopes) ? scopes.join(',') : scopes)}&` +
        `response_type=token&` +
        `key=${process.env.TRELLO_API_KEY}&` +
        `return_url=${encodeURIComponent(returnUrl)}`;

    return NextResponse.json({ url: authUrl });
}

export { POST as GET };