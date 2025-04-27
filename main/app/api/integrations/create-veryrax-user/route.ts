import { NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js'
import { randomBytes } from 'crypto';

function generatePassword(length = 16): string {
  const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+-=[]{}|;\':\",.<>/?';
  let password = '';
  const characterCount = characters.length;
  
  const randomValues = randomBytes(length);
  for (let i = 0; i < length; i++) {
    password += characters[randomValues[i] % characterCount];
  }
  return password;
}

export async function POST(request: Request) {
  const supabase = createClient(
    process.env.SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_KEY!
  );

  try {
    const { email } = await request.json();

    if (!email) {
      return NextResponse.json({ success: false, error: 'Email is required' }, { status: 400 });
    }

    const password = generatePassword();

    const { data: userData, error: userError } = await supabase.auth.admin.createUser({
      email: email,
      password: password,
      email_confirm: true,
    });

    if (userError) {
      console.error('Error creating Supabase user:', userError);
      const errorMessage = userError.message || 'Failed to create user';
      const status = userError.message.includes('already registered') ? 409 : 500;
      return NextResponse.json({ success: false, error: errorMessage }, { status });
    }

    if (!userData || !userData.user) {
       console.error('User data not returned after creation.');
       return NextResponse.json({ success: false, error: 'Failed to retrieve user data after creation' }, { status: 500 });
    }

    const userId = userData.user.id;

    const apiKeyBytes = randomBytes(20);
    const apiKey = 'vrx-' + apiKeyBytes.toString('hex');

    const { data: existingKey, error: selectError } = await supabase
      .from('users_api_keys')
      .select('id')
      .eq('user_id', userId)
      .maybeSingle();

    if (selectError && selectError.code !== 'PGRST116') { 
      console.error('Error checking for existing API key:', selectError);
      throw selectError;
    }

    let result;
    if (existingKey) {
      const { data, error: updateError } = await supabase
        .from('users_api_keys')
        .update({ api_key: apiKey })
        .eq('id', existingKey.id)
        .select()
        .single();
        
      if (updateError) {
        console.error('Error updating API key:', updateError);
        throw updateError;
      }
      result = data;
    } else {
      const { data, error: insertError } = await supabase
        .from('users_api_keys')
        .insert({ 
          api_key: apiKey,
          user_id: userId
        })
        .select()
        .single();
        
      if (insertError) {
        console.error('Error inserting new API key:', insertError);
        throw insertError;
      }
      result = data;
    }

    return NextResponse.json({ 
        success: true, 
        user_id: userId, 
        api_key_record: result 
    });

  } catch (error: any) {
    console.error('Error in create user/API key endpoint:', error);
    const message = error.message || 'Internal Server Error';
    const status = (error instanceof SyntaxError) ? 400 : 500; 
    return NextResponse.json({ success: false, error: message }, { status });
  }
}
