import { createClient } from '@/lib/utils/supabase/server';
import { createClient as createServiceClient } from '@supabase/supabase-js';
import { NextRequest, NextResponse } from 'next/server';
import crypto from 'crypto';

function generateRandomString(length: number): string {
    const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._';
    let text = '';
    
    const randomValues = crypto.randomBytes(length);
    for (let i = 0; i < length; i++) {
        text += possible.charAt(randomValues[i] % possible.length);
    }
    
    return text;
}

function generateCodeChallenge(codeVerifier: string): string {
    const hash = crypto.createHash('sha256').update(codeVerifier).digest();
    return hash.toString('base64')
        .replace(/\+/g, '-')
        .replace(/\//g, '_')
        .replace(/=/g, '');
}

export async function POST(request: NextRequest) {
    try {
        const { scopes = [], return_url, encrypted_api_key, code } = await request.json();
        
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
            .eq('provider_tag', 'airtable')
            .single();

        if (!provider) {
            return NextResponse.json({ error: 'Provider not found' }, { status: 404 });
        }
        
        const clientId = process.env.AIRTABLE_CLIENT_ID || '';

        const codeVerifier = generateRandomString(64);
        const codeChallenge = generateCodeChallenge(codeVerifier);

        const state = Buffer.from(JSON.stringify({
            provider_id: provider.id,
            scopes,
            code_verifier: codeVerifier,
            return_url: return_url || '/integrations',
            user_id,
            encrypted_api_key,
            code
        })).toString('base64');

        const redirectUri = `${request.nextUrl.origin}/api/oauth/airtable/callback`;
        
        
        const scopeString = Array.isArray(scopes) && scopes.length > 0 
            ? scopes.join(' ') 
            : 'data.records:read data.records:write schema.bases:read';
        
        const encodedRedirectUri = encodeURIComponent(redirectUri);
        const encodedScope = encodeURIComponent(scopeString);
        const encodedState = encodeURIComponent(state);
        const encodedChallenge = encodeURIComponent(codeChallenge);
        
        const authUrl = `https://airtable.com/oauth2/v1/authorize?` +
            `client_id=${encodeURIComponent(clientId)}` +
            `&response_type=code` +
            `&redirect_uri=${encodedRedirectUri}` +
            `&state=${encodedState}` +
            `&scope=${encodedScope}` +
            `&code_challenge=${encodedChallenge}` +
            `&code_challenge_method=S256`;
        
        
        return NextResponse.json({ url: authUrl });
    } catch (error) {
        return NextResponse.json({ 
            error: 'Failed to generate OAuth URL', 
            message: error instanceof Error ? error.message : 'Unknown error'
        }, { status: 500 });
    }
}

export { POST as GET };
