import Stripe from 'stripe';
import { createClient } from '@/lib/utils/supabase/server';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2025-03-31.basil' as any,
});

interface GetOrCreateCustomerParams {
  email: string;
  userId: string;
}

export async function getOrCreateCustomer({ email, userId }: GetOrCreateCustomerParams): Promise<string> {
  // Search for existing customer
  const existingCustomers = await stripe.customers.list({
    email: email,
    limit: 1
  });

  let customerId: string;

  if (existingCustomers.data.length > 0) {
    // Use existing customer
    customerId = existingCustomers.data[0].id;
    
    // Update metadata if needed
    if (!existingCustomers.data[0].metadata?.userId) {
      await stripe.customers.update(customerId, {
        metadata: {
          userId: userId
        }
      });
    }
  } else {
    // Create new customer if none exists
    const customer = await stripe.customers.create({
      email: email,
      metadata: {
        userId: userId
      }
    });
    customerId = customer.id;
  }

  // Update Supabase with customer ID
  const supabase = createClient();
  const { error: upsertError } = await supabase
    .from('users_stripe')
    .upsert({
      user_id: userId,
      stripe_customer_id: customerId
    }, { onConflict: 'user_id' });

  if (upsertError) {
    console.error('Error updating customer ID:', upsertError);
  }

  return customerId;
} 