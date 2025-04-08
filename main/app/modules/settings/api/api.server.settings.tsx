import { createClient } from '@/lib/utils/supabase/server';
import * as CoreApi from './api.core.settings';
import { fetch } from 'next/dist/compiled/@edge-runtime/primitives';
import { createClient as createServiceClient } from '@supabase/supabase-js';


// Серверные функции - обертки над ядром
export async function getUserSubscriptionServer() {
  return CoreApi.getUserSubscription(createClient());
}

export async function getUserUsageServer() {
  return CoreApi.getUserUsage(createClient());
}

export async function getUserProductInfoServer() {
  return CoreApi.getUserProductInfo(createClient());
}

export async function isUserOnFreePlanServer() {
  return CoreApi.isUserOnFreePlan(createClient());
}

export async function canUserCreateFlowServer(increment: number = 1) {
  return CoreApi.canUserCreateFlow(createClient(), increment);
}

export async function canUserSendMessageServer(increment: number = 1) {
  return CoreApi.canUserSendMessage(createClient(), increment);
}

export async function canUserCallAPIServer(increment: number = 1) {
  return CoreApi.canUserCallAPI(createClient(), increment);
}

export async function getUserApiKeyServer() {
  return CoreApi.getUserApiKey(createClient());
}

export async function revokeApiKeyServer() {
  return CoreApi.revokeApiKey(createClient());
}

export async function deleteUserAccountServer() {
  return CoreApi.deleteUserAccount(createClient(), fetch);
}

export async function canUserRentKeyServer(userId: string) {
  try {
    const client = createServiceClient(
      process.env.SUPABASE_URL!,
      process.env.SUPABASE_SERVICE_KEY!
    );

    const { data: subscription } = await client
      .from('user_subscriptions_view')
      .select('*')
      .eq('user_id', userId)
      .single();
    
    let productInfo;
    if (!subscription || subscription.subscription_status !== 'active') {
      const { data } = await client
        .from('products_info')
        .select('*')
        .eq('product_tag', 'free')
        .single();

      productInfo = data;
    } else {
      const { data } = await client
        .from('products_info')
        .select('*')
        .eq('stripe_product_id', subscription.product_id)
        .single();

      productInfo = data;
    }

    if (!productInfo) {
      return { 
        allowed: false, 
        reason: 'Could not fetch user plan information'
      };
    }

    const canRentKeys = productInfo.attrs?.rent_provider_keys || false;
    
    return {
      allowed: canRentKeys,
      reason: !canRentKeys ? 'Your current plan does not allow renting provider keys' : undefined
    };
  } catch (error) {
    console.error('Error checking key rental permission:', error);
    return { allowed: false, reason: 'Error checking permissions' };
  }
} 