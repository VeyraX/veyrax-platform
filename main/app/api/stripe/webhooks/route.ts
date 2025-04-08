import { NextRequest, NextResponse } from 'next/server';
import Stripe from 'stripe';
import { headers } from 'next/headers';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2025-03-31.basil' as any,
});

const webhookSecret = process.env.TEST_STRIPE_WEBHOOK_SECRET!;

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
      console.error(`Webhook signature verification failed: ${err}`);
      return NextResponse.json(
        { message: `Webhook Error: ${err.message}` },
        { status: 400 }
      );
    }

    switch (event.type) {
      case 'checkout.session.completed':
        const session = event.data.object as Stripe.Checkout.Session;
        
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