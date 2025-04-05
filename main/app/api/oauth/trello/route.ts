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
        .select('id, provider_tag')
        .eq('provider_tag', 'trello')
        .single();

    if (!provider) {
        return NextResponse.json({ error: 'Provider not found' }, { status: 404 });
    }

    const authCompleteUrl = `${request.nextUrl.origin}/user/${provider.provider_tag}/auth/auth-complete`;
    const finalReturnUrl = return_url || '/integrations';
    
    const stateData = {
        user_id,
        encrypted_api_key,
        code,
        return_url: finalReturnUrl
    };
    const stateParam = Buffer.from(JSON.stringify(stateData)).toString('base64');
    
    const fullReturnUrl = `${authCompleteUrl}?return_to=${finalReturnUrl}&state=${stateParam}`;
    
    const encodedReturnUrl = encodeURIComponent(fullReturnUrl);
    
    const authUrl = `https://trello.com/1/authorize?` +
        `expiration=never&` +
        `name=Veyrax&` +
        `scope=${encodeURIComponent(Array.isArray(scopes) ? scopes.join(',') : scopes)}&` +
        `response_type=token&` +
        `key=${process.env.TRELLO_API_KEY}&` +
        `return_url=${encodedReturnUrl}`;

    return NextResponse.json({ url: authUrl });
}

export { POST as GET };