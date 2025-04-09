import { NextRequest, NextResponse } from 'next/server';
import Stripe from 'stripe';
import { headers } from 'next/headers';
import { Resend } from 'resend';
import SubscriptionConfirmationEmail from '@/app/modules/email/templates/subscription-confirmation';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2025-03-31.basil' as any,
});

const resend = new Resend(process.env.RESEND_API_KEY);

const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET!.replace('hsec_', 'whsec_');

export const dynamic = 'force-dynamic';
export const runtime = 'nodejs';

export const fetchCache = 'force-no-store';
export const revalidate = 0;

export async function POST(req: NextRequest) {
  
  let event: Stripe.Event;
  
  try {
    const body = await req.text();
    const signature = headers().get('stripe-signature')!;
    
    try {
      event = stripe.webhooks.constructEvent(
        body,
        signature,
        webhookSecret
      );
    } catch (err: any) {
      return NextResponse.json(
        { message: `Webhook Error: ${err.message}` },
        { status: 400 }
      );
    }

    switch (event.type) {
      case 'checkout.session.completed':
        const session = event.data.object as Stripe.Checkout.Session;
        
        try {
          const customerEmail = session.customer_details?.email;
          
          if (customerEmail) {
            
            const emailResult = await resend.emails.send({
              from: 'service@veyrax.com',
              to: customerEmail,
              subject: 'Your VeyraX Subscription Confirmation',
              react: SubscriptionConfirmationEmail(),
            });

            
            if (emailResult.error) {
              console.error('Error sending confirmation email:', emailResult.error);
            } else {
              console.log('Confirmation email sent successfully', emailResult.data);
            }
          } else {
            console.warn('No customer email found in checkout session');
          }
        } catch (emailError) {
          console.error('Failed to send confirmation email:', emailError);
        }
        
        break;
      
      case 'payment_intent.succeeded':
        const paymentIntent = event.data.object as Stripe.PaymentIntent;
        console.log(`PaymentIntent succeeded: ${paymentIntent.id}`);
        break;
        
      case 'payment_intent.payment_failed':
        const failedPaymentIntent = event.data.object as Stripe.PaymentIntent;
        console.log(`PaymentIntent failed: ${failedPaymentIntent.id}`);
        break;
        
      default:
        console.log(`Unhandled event type: ${event.type}`);
    }

    return NextResponse.json({ received: true });
  } catch (err) {
    console.error('Webhook error:', err);
    return NextResponse.json(
      { message: 'Webhook handler failed' },
      { status: 500 }
    );
  }
} 