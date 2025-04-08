import { NextRequest, NextResponse } from 'next/server';
import Stripe from 'stripe';
import { createClient } from '@/lib/utils/supabase/server';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2025-03-31.basil' as any,
});

export async function POST(req: NextRequest) {
  try {
    const supabase = createClient();
    
    const { data: { user }, error: userError } = await supabase.auth.getUser();
    
    if (userError || !user) {
      return NextResponse.json(
        { message: 'Unauthorized' },
        { status: 401 }
      );
    }
    
    const body = await req.json();
    const { priceId } = body;
    
    if (!priceId) {
      return NextResponse.json(
        { message: 'Price ID is required' },
        { status: 400 }
      );
    }

    const customer = await stripe.customers.create({
      email: user.email,
      metadata: {
        userId: user.id
      }
    });
    
    const customerId = customer.id;
    
    const { error: upsertError } = await supabase
      .from('users_stripe')
      .upsert({
        user_id: user.id,
        stripe_customer_id: customerId
      }, { onConflict: 'user_id' });
    
    if (upsertError) {
      console.error('Error updating customer ID:', upsertError);
    }

    const params: Stripe.Checkout.SessionCreateParams = {
      mode: 'subscription',
      customer: customerId,
      payment_method_types: ['card'],
      line_items: [
        {
          price: priceId,
          quantity: 1,
        },
      ],
      success_url: `${req.headers.get('origin')}/pricing/success?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${req.headers.get('origin')}/pricing?canceled=true`,
      metadata: {
        userId: user.id
      },
    };

    const checkoutSession = await stripe.checkout.sessions.create(params);

    return NextResponse.json({ sessionId: checkoutSession.id });
  } catch (error) {
    console.error('Error creating checkout session:', error);
    return NextResponse.json(
      { message: 'Error creating checkout session' },
      { status: 500 }
    );
  }
} 