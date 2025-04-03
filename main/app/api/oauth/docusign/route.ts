import { createClient } from '@/lib/utils/supabase/server';
import { NextRequest, NextResponse } from 'next/server';
import crypto from 'crypto';

// Function to generate code verifier
function generateCodeVerifier() {
    return crypto.randomBytes(32)
        .toString('base64')
        .replace(/\+/g, '-')
        .replace(/\//g, '_')
        .replace(/=/g, '');
}

// Function to generate code challenge from verifier
function generateCodeChallenge(verifier: string) {
    const hash = crypto.createHash('sha256')
        .update(verifier)
        .digest('base64')
        .replace(/\+/g, '-')
        .replace(/\//g, '_')
        .replace(/=/g, '');
    return hash;
}

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
        .eq('provider_tag', 'docusign')
        .single();

    if (!provider) {
        return NextResponse.json({ error: 'Provider not found' }, { status: 404 });
    }

    // Generate PKCE values
    const codeVerifier = generateCodeVerifier();
    const codeChallenge = generateCodeChallenge(codeVerifier);

    const state = Buffer.from(JSON.stringify({
        provider_id: provider.id,
        scopes,
        return_url: return_url || '/integrations',
        code_verifier: codeVerifier // Store code verifier in state for callback
    })).toString('base64');

    const redirectUri = `${request.nextUrl.origin}/api/oauth/docusign/callback`;

    const authUrl = `https://account.docusign.com/oauth/auth?` +
        `client_id=${process.env.DOCUSIGN_CLIENT_ID}&` +
        `redirect_uri=${encodeURIComponent(redirectUri)}&` +
        `scope=${encodeURIComponent(Array.isArray(scopes) ? scopes.join(' ') : scopes)}&` +
        `state=${state}&` +
        `response_type=code&` +
        `code_challenge=${encodeURIComponent(codeChallenge)}&` +
        `code_challenge_method=S256`;

    return NextResponse.json({ url: authUrl });
}

export { POST as GET };
