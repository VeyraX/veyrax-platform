import { NextResponse } from 'next/server';
import { createClient, SupabaseClient } from '@supabase/supabase-js'
import { randomBytes } from 'crypto';

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
    console.log(`API key already exists for user ${userId}.`);
    return existingKey;
  }

  console.log(`No API key found for user ${userId}. Generating a new one.`);
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

  console.log(`Successfully created new API key for user ${userId}.`);
  return newKey;
}

export async function POST(request: Request) {
  const supabase = createClient(
    process.env.SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_KEY!
  );

  try {
    const { omi_user_id } = await request.json();

    if (!omi_user_id) {
      return NextResponse.json({ success: false, error: 'omi_user_id is required' }, { status: 400 });
    }

    const { data: existingOmiUser, error: omiCheckError } = await supabase
      .from('omi_users')
      .select('user_id')
      .eq('omi_user_id', omi_user_id)
      .maybeSingle();

    if (omiCheckError) {
      console.error(`Error checking omi_users table for omi_user_id ${omi_user_id}:`, omiCheckError);
      throw omiCheckError;
    }

    let userId: string;
    let apiKeyRecord: any;
    let message: string;

    if (existingOmiUser && existingOmiUser.user_id) {
      userId = existingOmiUser.user_id;
      console.log(`omi_user ${omi_user_id} already linked to Supabase user ${userId}. Ensuring API key exists.`);
      apiKeyRecord = await ensureApiKeyForUser(supabase, userId);
      message = "User already exists, API key ensured.";

    } else {
      console.log(`omi_user ${omi_user_id} not found in omi_users. Creating new Supabase user.`);
      const generatedEmail = `omi_user_${omi_user_id}@example.io`;
      const password = generatePassword();

      const { data: userData, error: userError } = await supabase.auth.admin.createUser({
        email: generatedEmail,
        password: password,
        email_confirm: true,
      });

      if (userError) {
        console.error('Error creating Supabase user:', userError);
        const isConflict = userError.message.includes('already registered') || userError.message.includes('User already registered');
        const errorMessage = userError.message || 'Failed to create Supabase user';
        const status = isConflict ? 409 : 500;
        return NextResponse.json({ success: false, error: errorMessage }, { status });
      }

      if (!userData || !userData.user) {
         console.error('Supabase user data not returned after creation.');
         return NextResponse.json({ success: false, error: 'Failed to retrieve user data after creation' }, { status: 500 });
      }

      userId = userData.user.id;
      console.log(`Created new Supabase user ${userId} for omi_user ${omi_user_id}.`);

      const { error: omiInsertError } = await supabase
        .from('omi_users')
        .insert({ omi_user_id: omi_user_id, user_id: userId });

      if (omiInsertError) {
        console.error(`CRITICAL: Failed to link omi_user ${omi_user_id} to Supabase user ${userId} in omi_users table:`, omiInsertError);
        throw omiInsertError;
      } else {
        console.log(`Successfully linked omi_user ${omi_user_id} to Supabase user ${userId}.`);
      }

      apiKeyRecord = await ensureApiKeyForUser(supabase, userId);
      message = "New user created, linked, and API key ensured.";
    }

    return NextResponse.json({
        success: true,
        message: message,
        user_id: userId,
        omi_user_id: omi_user_id,
        api_key_record: apiKeyRecord
    });

  } catch (error: any) {
    console.error('Error in /create-veryrax-user endpoint:', error);
    const message = error.message || 'Internal Server Error';
    const status = (error instanceof SyntaxError) ? 400 : 500;
    return NextResponse.json({ success: false, error: message }, { status });
  }
}
