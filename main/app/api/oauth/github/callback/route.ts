import { createClient } from '@/lib/utils/supabase/server';
import { NextRequest, NextResponse } from 'next/server';
import { encrypt } from '@/lib/utils/encryption';

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const code = searchParams.get('code');
  const state = searchParams.get('state');

  if (!code || !state) {
    console.error('Missing code or state');
    return NextResponse.redirect(`${request.nextUrl.origin}/integrations?error=Invalid request`);
  }

  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();

  if (!user) {
    console.error('No user found');
    return NextResponse.redirect(`${request.nextUrl.origin}/integrations?error=Unauthorized`);
  }

  try {
    const decodedState = Buffer.from(state, 'base64').toString();
    const { provider_id, scopes } = JSON.parse(decodedState);

    const { data: provider, error: providerError } = await supabase
      .from('providers')
      .select('*')
      .eq('id', provider_id)
      .single();

    if (providerError || !provider) {
      console.error('Provider error:', providerError);
      throw new Error('Provider not found');
    }

    const redirectUri = `${request.nextUrl.origin}/api/oauth/github/callback`;

    const tokenResponse = await fetch('https://github.com/login/oauth/access_token', {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        client_id: process.env.GITHUB_CLIENT_ID,
        client_secret: process.env.GITHUB_CLIENT_SECRET,
        code,
        redirect_uri: redirectUri,
        state,
      }),
    });

    const tokens = await tokenResponse.json();

    if (tokens.error) {
      console.error('Token error:', tokens);
      throw new Error(tokens.error_description || tokens.error);
    }

    const encryptedAccessToken = encrypt(tokens.access_token);
    
    const encryptedTokenData = {
      ...tokens,
      access_token: encryptedAccessToken
    };

    const { error: providerUpsertError } = await supabase
      .from('users_providers')
      .upsert({
        user_id: user.id,
        provider_id: provider_id
      }, {
        onConflict: 'user_id,provider_id'
      });

    if (providerUpsertError) {
      console.error('Provider upsert error:', providerUpsertError);
      throw providerUpsertError;
    }

    const { error: upsertError } = await supabase
      .from('users_oauth_tokens')
      .upsert({
        user_id: user.id,
        provider_id: provider_id,
        access_token: encryptedAccessToken,
        refresh_token: null,
        expires_at: null,
        scopes: Array.isArray(scopes) ? scopes.join(',') : scopes,
        raw_token_data: encryptedTokenData,
      }, {
        onConflict: 'user_id,provider_id'
      });

    if (upsertError) {
      console.error('Upsert error:', upsertError);
      throw upsertError;
    }

    return NextResponse.redirect(`${request.nextUrl.origin}/integrations?success=true`);
  } catch (error: any) {
    console.error('OAuth callback error:', {
      message: error.message,
      error: error
    });
    return NextResponse.redirect(
      `${request.nextUrl.origin}/integrations?error=${encodeURIComponent(error.message || 'Unknown error')}`
    );
  }
}