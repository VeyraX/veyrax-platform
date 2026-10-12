import { NextRequest, NextResponse } from 'next/server';
import Stripe from 'stripe';
import { headers } from 'next/headers';
import { Resend } from 'resend';
import SubscriptionConfirmationEmail from '@/app/modules/email/templates/subscription-confirmation';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2025-03-31.basil' as any,
});

const resend = new Resend(process.env.RESEND_API_KEY);

const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET!;

export const dynamic = 'force-dynamic';
export const runtime = 'nodejs';

export const fetchCache = 'force-no-store';
export const revalidate = 0;

export async function POST(req: NextRequest) {
  
  let event: Stripe.Event;
  
  try {
    const body = await req.text();
    const signature = headers().get('stripe-signature');
    
    if (!signature) {
      console.error('No stripe-signature header found');
      return NextResponse.json(
        { message: 'No stripe signature found in request headers' },
        { status: 400 }
      );
    }

    try {
      event = stripe.webhooks.constructEvent(
        body,
        signature,
        webhookSecret
      );
    } catch (err: any) {
      console.error('Webhook signature verification failed:', {
        error: err.message,
        signatureHeader: signature,
      });
      return NextResponse.json(
        { message: `Webhook Error: ${err.message}` },
        { status: 400 }
      );
    }

    switch (event.type) {
      case 'checkout.session.completed':
        const session = event.data.object as Stripe.Checkout.Session;
        
        if (session.payment_status !== 'paid') {
          console.warn(`Checkout completed but payment not successful. Status: ${session.payment_status}`);
          break;
        }
        
        try {
          const customerEmail = session.customer_details?.email;
          
          if (customerEmail) {
            
            const emailResult = await resend.emails.send({
              from: process.env.RESEND_FROM_EMAIL || 'noreply@localhost',
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

      case 'invoice.payment_succeeded':
        const invoice = event.data.object as Stripe.Invoice;
        const customerEmail = invoice.customer_email;
        console.log(`Invoice paid: ${invoice.id}`);
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