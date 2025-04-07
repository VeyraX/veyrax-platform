import { NextRequest, NextResponse } from 'next/server';
import Stripe from 'stripe';

const stripe = new Stripe(process.env.TEST_STRIPE_SECRET_KEY!, {
  apiVersion: '2025-03-31.basil' as any,
});

export async function GET(
  req: NextRequest, 
  { params }: { params: { id: string } }
) {
  try {
    const id = params.id;
    
    if (!id.startsWith('cs_')) {
      return NextResponse.json(
        { error: 'Invalid session ID' },
        { status: 400 }
      );
    }

    const session = await stripe.checkout.sessions.retrieve(id, {
      expand: ['payment_intent', 'line_items'],
    });

    return NextResponse.json({
      status: session.status,
      customer_email: session.customer_details?.email || '',
      amount_total: session.amount_total,
      currency: session.currency,
      payment_status: session.payment_status,
      items: session.line_items?.data.map(item => ({
        description: item.description,
        amount: item.amount_total,
      })),
    });
  } catch (error) {
    console.error('Error retrieving session:', error);
    return NextResponse.json(
      { error: 'Error retrieving session' },
      { status: 500 }
    );
  }
} 