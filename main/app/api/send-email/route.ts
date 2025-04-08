import { NextResponse } from 'next/server';
import { Resend } from 'resend';
import SubscriptionConfirmationEmail from '@/app/modules/email/templates/subscription-confirmation';

const resend = new Resend(process.env.RESEND_API_KEY);

export async function POST(request: Request) {
  try {
    const { email } = await request.json();
    
    if (!email) {
      return NextResponse.json(
        { error: 'Email address is required' },
        { status: 400 }
      );
    }
    
    const data = await resend.emails.send({
      from: 'onboarding@resend.dev',
      to: email,
      subject: 'Your VeyraX Subscription Confirmation',
      react: SubscriptionConfirmationEmail(),
    });
    
    return NextResponse.json(data);
  } catch (error) {
    return NextResponse.json({ error }, { status: 500 });
  }
} 