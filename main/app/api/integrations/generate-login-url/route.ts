import { NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';
import { z } from 'zod';

const requestBodySchema = z.object({
  omi_user_id: z.string(),
});

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
      return NextResponse.json({ success: false, error: `No Veyrax user found for omi_user_id: ${omi_user_id}` }, { status: 404 });
    }

    const userId = omiUser.user_id;
    const userEmail = `omi_user_${omi_user_id}@example.io`;

    const { data: linkData, error: linkError } = await supabase.auth.admin.generateLink({
        type: 'magiclink',
        email: userEmail,
        options: {
          redirectTo: `${process.env.FRONTEND_URL}/integrations/`
        }
    });

    if (linkError) {
      if (linkError.message.includes("Email not confirmed")) {
         return NextResponse.json({ success: false, error: 'User email not confirmed. Cannot generate session directly.' }, { status: 400 });
      }
       return NextResponse.json({ success: false, error: 'Failed to generate link/session.' }, { status: 500 });
    }

    const properties = linkData.properties;
    if (properties && properties.hashed_token) {
       return NextResponse.json({
          success: true,
          link: properties.action_link,
          hashed_token: properties.hashed_token,
          user: linkData.user
       });
     } else {
       console.error(`Failed to extract link properties for user ${userId}. Response data:`, JSON.stringify(linkData, null, 2));
       return NextResponse.json({ success: false, error: 'Failed to generate necessary link properties.' }, { status: 500 });
     }

  } catch (error: any) {
    const message = error.message || 'Internal Server Error';
    const status = (error instanceof SyntaxError) ? 400 : (error.code === 'PGRST116' || error.status === 404) ? 404 : 500;
    return NextResponse.json({ success: false, error: message }, { status });
  }
}
