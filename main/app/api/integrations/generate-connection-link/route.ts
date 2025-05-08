import { NextResponse } from 'next/server';
import { createClient, SupabaseClient } from '@supabase/supabase-js';
import { z } from 'zod';
import { randomBytes } from 'crypto';

const requestBodySchema = z.object({
  omi_user_id: z.string(),
  provider_tag: z.string(),
  type: z.string().optional(),
  redirect_url: z.string().optional(),
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

async function ensureApiKeyForUser(supabase: SupabaseClient, userId: string): Promise<{ user_id: string, api_key: string } | null> {
  const { data: existingKey, error: selectError } = await supabase
    .from('users_api_keys')
    .select('user_id, api_key')
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
    .select('user_id, api_key')
    .single();

  if (insertError) {
    console.error(`Error inserting new API key for user ${userId}:`, insertError);
    throw insertError;
  }

  if (!newKey) {
     console.error(`API key record not returned after insertion for user ${userId}.`);
     throw new Error('Failed to retrieve API key after creation');
  }

  return newKey;
}

async function getOrCreateUserAndApiKey(supabase: SupabaseClient, omi_user_id: string): Promise<{ user_id: string, api_key: string }> {
  const userEmail = `omi_user_${omi_user_id}@example.io`;
  let userId: string;
  let apiKeyRecord: { user_id: string, api_key: string } | null;

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
       if (userError.message.includes('already registered')) {
         throw new Error(`User with email ${userEmail} already exists but is not linked to omi_user_id ${omi_user_id}. Please check linkage.`);
       }
      throw userError;
    }

    if (!userData || !userData.user) {
       throw new Error('Failed to retrieve user data after creation');
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

  } else {
    userId = omiUser.user_id;
    apiKeyRecord = await ensureApiKeyForUser(supabase, userId);
  }

  if (!apiKeyRecord) {
      throw new Error(`Could not ensure API key for user ${userId}`);
  }

  return apiKeyRecord;
}

export async function POST(request: Request) {
  const supabase = createClient(
    process.env.SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_KEY!
  );

  const aciServerUrl = process.env.ACI_SERVER_URL || 'http://localhost:8000';

  try {
    const rawBody = await request.json();
    const validationResult = requestBodySchema.safeParse(rawBody);

    if (!validationResult.success) {
      return NextResponse.json(
        { error: 'Invalid request body', details: validationResult.error.flatten() },
        { status: 400 }
      );
    }
    
    const { omi_user_id, provider_tag, type = 'tool', redirect_url: frontendRedirectUrl } = validationResult.data; 

    const { user_id, api_key } = await getOrCreateUserAndApiKey(supabase, omi_user_id);

    const backendUrl = `${aciServerUrl}/tool-call/veyrax-auth/generate_connection_link`;
    const promptMessage = `Paste this UID in ChatGPT ${omi_user_id} =>`;
    const redirectUrl = frontendRedirectUrl || `https://chatgpt.com/g/g-67e2772d0af081919a5baddf4a12aacf-omigpt?prompt=${encodeURIComponent(promptMessage)}`;
    const backendPayload = {
      provider_tag: provider_tag,
      type: type,
      redirect_url: redirectUrl,
    };

    const backendResponse = await fetch(backendUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'VEYRAX_API_KEY': `${api_key}`,
      },
      body: JSON.stringify(backendPayload),
      redirect: 'manual' 
    });

    console.log(`Backend returned status: ${backendResponse.status}`);

    return new NextResponse(backendResponse.body, {
      status: backendResponse.status,
      statusText: backendResponse.statusText,
      headers: backendResponse.headers,
    });

  } catch (error: any) {
    console.error('Error in /generate-connection-link proxy:', error);
    let message = 'Internal Server Error';
    let status = 500;

    if (error instanceof SyntaxError) { // Error parsing initial request JSON
        message = 'Invalid request body format';
        status = 400;
    } else if (error.message.includes('already exists but is not linked')) {
        message = error.message;
        status = 409;
    } else if (error.code === 'PGRST116') { // Error finding user during getOrCreateUserAndApiKey
        message = 'User lookup failed'; // More generic message for client
        status = 404; 
    } else if (error.cause instanceof Error && error.cause.code === 'ECONNREFUSED') {
        message = 'Could not connect to backend service.';
        status = 503; // Service Unavailable
    } else {
        message = error.message || message;
    }

    return NextResponse.json({ error: message }, { status });
  }
}
