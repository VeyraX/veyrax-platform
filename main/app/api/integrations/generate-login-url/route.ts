import { NextResponse } from 'next/server';
import { createClient, SupabaseClient } from '@supabase/supabase-js';
import { z } from 'zod';
import { randomBytes } from 'crypto';

const requestBodySchema = z.object({
  omi_user_id: z.string(),
});

function generatePassword(length = 16): string {
  const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+-=[]{}|;\':",.<>/?';
  let password = '';
  const characterCount = characters.length;

  const randomValues = randomBytes(length);
  for (let i = 0; i < length; i++) {
    password += characters[randomValues[i] % characterCount];
  }
  return password;
}

async function ensureApiKeyForUser(supabase: SupabaseClient, userId: string): Promise<any> {
  const { data: existingKey, error: selectError } = await supabase
    .from('users_api_keys')
    .select('*')
    .eq('user_id', userId)
    .maybeSingle();

  if (selectError && selectError.code !== 'PGRST116') {
    console.error(`Error checking for existing API key for user ${userId}:`, selectError);
    throw selectError;
  }

  if (existingKey) {
    return existingKey;
  }

  const apiKeyBytes = randomBytes(20);
  const apiKey = 'vrx-' + apiKeyBytes.toString('hex');

  const { data: newKey, error: insertError } = await supabase
    .from('users_api_keys')
    .insert({
      api_key: apiKey,
      user_id: userId
    })
    .select()
    .single();

  if (insertError) {
    console.error(`Error inserting new API key for user ${userId}:`, insertError);
    throw insertError;
  }

  return newKey;
}

export async function POST(request: Request) {
  const supabase = createClient(
    process.env.SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_KEY!,
    {
      auth: {
        persistSession: false,
        autoRefreshToken: false,
        detectSessionInUrl: false,
      },
    }
  );

  try {
    const rawBody = await request.json();
    const validationResult = requestBodySchema.safeParse(rawBody);

    if (!validationResult.success) {
      return NextResponse.json({ success: false, error: 'Invalid request body', details: validationResult.error.flatten() }, { status: 400 });
    }

    const { omi_user_id } = validationResult.data;
    const userEmail = `omi_user_${omi_user_id}@example.io`;

    let userId: string;
    let apiKeyRecord: any;
    let message: string;

    const { data: omiUser, error: omiCheckError } = await supabase
      .from('omi_users')
      .select('user_id')
      .eq('omi_user_id', omi_user_id)
      .maybeSingle();

    if (omiCheckError) {
      console.error(`Error fetching omi_user mapping for ${omi_user_id}:`, omiCheckError);
      throw omiCheckError;
    }

    if (!omiUser || !omiUser.user_id) {
      const password = generatePassword();

      const { data: userData, error: userError } = await supabase.auth.admin.createUser({
        email: userEmail,
        password: password,
        email_confirm: true,
      });

      if (userError) {
        console.error('Error creating Supabase user:', userError);
        const isConflict = userError.message.includes('already registered') || userError.message.includes('User already registered');
        const errorMessage = userError.message || 'Failed to create Supabase user';
        const status = isConflict ? 409 : 500;
        if (isConflict) {
           return NextResponse.json({ success: false, error: `User with email ${userEmail} already exists but is not linked to omi_user_id ${omi_user_id}. Please check linkage.` }, { status });
        }
        return NextResponse.json({ success: false, error: errorMessage }, { status });
      }

      if (!userData || !userData.user) {
         console.error('Supabase user data not returned after creation.');
         return NextResponse.json({ success: false, error: 'Failed to retrieve user data after creation' }, { status: 500 });
      }

      userId = userData.user.id;

      const { error: omiInsertError } = await supabase
        .from('omi_users')
        .insert({ omi_user_id: omi_user_id, user_id: userId });

      if (omiInsertError) {
        console.error(`CRITICAL: Failed to link omi_user ${omi_user_id} to Supabase user ${userId} in omi_users table:`, omiInsertError);
        throw omiInsertError;
      }

      apiKeyRecord = await ensureApiKeyForUser(supabase, userId);
      message = "New user created, linked, API key ensured, and login link generated.";

    } else {
      userId = omiUser.user_id;
      apiKeyRecord = await ensureApiKeyForUser(supabase, userId);
      message = "Existing user found, API key ensured, and login link generated.";
    }

    const { data: linkData, error: linkError } = await supabase.auth.admin.generateLink({
        type: 'magiclink',
        email: userEmail,
        options: {
          redirectTo: `${process.env.FRONTEND_URL}/auth/callback?next=/integrations`
        }
    });

    if (linkError) {
       console.error(`Error generating magic link for user ${userId}:`, linkError);
       return NextResponse.json({ success: false, error: 'Failed to generate magic link.' }, { status: 500 });
    }

    if (linkData?.properties?.action_link) {
      const actionLink = new URL(linkData.properties.action_link);

      // Transfer tokens from hash to query
      const fragment = new URLSearchParams(actionLink.hash.replace('#', ''));
      fragment.forEach((value, key) => {
        actionLink.searchParams.set(key, value);
      });
      
      // Ensure we have a next parameter in both places for good measure
      // Adding directly to hash for clients that might inspect it
      fragment.set('next', '/integrations');
      actionLink.hash = fragment.toString();
      
      // Also set in query params for our callback handler
      actionLink.searchParams.set('next', '/integrations');

      return NextResponse.json({
        success: true,
        link: actionLink.toString(),
        omi_user_id: omi_user_id,
      });
    } else {
      console.error(`Failed to extract link properties for user ${userId}. Response data:`, JSON.stringify(linkData, null, 2));
      return NextResponse.json({ success: false, error: 'Failed to generate necessary link properties.' }, { status: 500 });
    }

  } catch (error: any) {
    console.error('Error in /generate-login-url endpoint:', error);
    const message = error.message || 'Internal Server Error';
    const status = (error instanceof SyntaxError) ? 400 : (error.code === 'PGRST116') ? 404 : 500;
    return NextResponse.json({ success: false, error: message }, { status });
  }
}
