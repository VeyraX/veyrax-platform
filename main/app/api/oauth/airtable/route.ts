import { createClient } from '@/lib/utils/supabase/server';
import { NextRequest, NextResponse } from 'next/server';
import crypto from 'crypto';

// Function to generate a random string for code_verifier
function generateRandomString(length: number): string {
    const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~';
    let text = '';
    
    const randomValues = crypto.randomBytes(length);
    for (let i = 0; i < length; i++) {
        text += possible.charAt(randomValues[i] % possible.length);
    }
    
    return text;
}

// Function to create code_challenge from code_verifier
function generateCodeChallenge(codeVerifier: string): string {
    const hash = crypto.createHash('sha256').update(codeVerifier).digest();
    return hash.toString('base64')
        .replace(/\+/g, '-')
        .replace(/\//g, '_')
        .replace(/=/g, '');
}

export async function POST(request: NextRequest) {
    try {
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

        console.log('Provider data:', provider);
        console.log('Client ID exists:', !!process.env.AIRTABLE_CLIENT_ID);
        console.log('Client Secret exists:', !!process.env.AIRTABLE_CLIENT_SECRET);
        console.log('Requested scopes:', scopes);

        const codeVerifier = generateRandomString(64);
        const codeChallenge = generateCodeChallenge(codeVerifier);

        const state = Buffer.from(JSON.stringify({
            provider_id: provider.id,
            scopes,
            code_verifier: codeVerifier
        })).toString('base64');

        const redirectUri = `${request.nextUrl.origin}/api/oauth/airtable/callback`;
        
        console.log('Request origin:', request.nextUrl.origin);
        console.log('Redirect URI:', redirectUri);
        
        const scopeString = Array.isArray(scopes) && scopes.length > 0 
            ? scopes.join(' ') 
            : 'data.records:read data.records:write schema.bases:read';

        if (!process.env.AIRTABLE_CLIENT_ID) {
            return NextResponse.json({ error: 'Airtable CLIENT_ID not configured' }, { status: 500 });
        }

        const params = new URLSearchParams();
        params.set('client_id', process.env.AIRTABLE_CLIENT_ID);
        params.set('response_type', 'code');
        params.set('redirect_uri', redirectUri);
        params.set('state', state);
        params.set('scope', scopeString);
        // Add PKCE parameters
        params.set('code_challenge', codeChallenge);
        params.set('code_challenge_method', 'S256');

        const authUrl = `https://airtable.com/oauth2/v1/authorize?${params.toString()}`;
        
        console.log('Generated auth URL with PKCE');
        
        return NextResponse.json({ url: authUrl });
    } catch (error) {
        console.error('OAuth URL generation error:', error);
        return NextResponse.json({ 
            error: 'Failed to generate OAuth URL', 
            message: error instanceof Error ? error.message : 'Unknown error'
        }, { status: 500 });
    }
}

export { POST as GET };
