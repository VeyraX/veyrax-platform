import { SupabaseClient } from '@supabase/supabase-js';
import { UserProfile, UserApiKey, UserSubscription } from './types.settings';

// Общие функции для работы с настройками пользователя
export async function getUserProfile(supabase: SupabaseClient): Promise<UserProfile | null> {
  try {
    const { data: { user }, error } = await supabase.auth.getUser();
    if (error || !user) {
      return null;
    }

    return {
      id: user.id,
      email: user.email ?? null,
      full_name: user.user_metadata?.full_name ?? null,
      avatar_url: user.user_metadata?.picture ?? user.user_metadata?.avatar_url ?? null,
    };
  } catch (error) {
    console.error('Error in getUserProfile:', error);
    return null;
  }
}

export async function getUserApiKey(supabase: SupabaseClient): Promise<UserApiKey | null> {
  try {
    const { data: { user }, error: userError } = await supabase.auth.getUser();
    if (userError || !user) {
      return null;
    }

    const { data, error } = await supabase
      .from('users_api_keys')
      .select('*')
      .eq('user_id', user.id)
      .single();

    if (error) {
      console.error('Error fetching API key:', error);
      return null;
    }

    return data;
  } catch (error) {
    console.error('Error in getUserApiKey:', error);
    return null;
  }
}

export async function generateApiKey(supabase: SupabaseClient, getRandomBytes: () => Uint8Array): Promise<UserApiKey | null> {
  try {
    const { data: { user }, error: userError } = await supabase.auth.getUser();
    if (userError || !user) {
      return null;
    }

    const randomBytes = getRandomBytes();
    const apiKey = 'vrx-' + Array.from(randomBytes)
      .map(b => b.toString(16).padStart(2, '0'))
      .join('');

    const { data: existingKey } = await supabase
      .from('users_api_keys')
      .select('id')
      .eq('user_id', user.id)
      .single();

    let result;
    
    if (existingKey) {
      const { data, error } = await supabase
        .from('users_api_keys')
        .update({ api_key: apiKey })
        .eq('id', existingKey.id)
        .select()
        .single();
        
      if (error) throw error;
      result = data;
    } else {
      const { data, error } = await supabase
        .from('users_api_keys')
        .insert({ 
          api_key: apiKey,
          user_id: user.id
        })
        .select()
        .single();
        
      if (error) throw error;
      result = data;
    }

    return result;
  } catch (error) {
    console.error('Error generating API key:', error);
    return null;
  }
}

export async function revokeApiKey(supabase: SupabaseClient): Promise<boolean> {
  try {
    const { data: { user }, error: userError } = await supabase.auth.getUser();
    if (userError || !user) {
      return false;
    }

    const { error } = await supabase
      .from('users_api_keys')
      .delete()
      .eq('user_id', user.id);

    if (error) {
      console.error('Error revoking API key:', error);
      return false;
    }

    return true;
  } catch (error) {
    console.error('Error in revokeApiKey:', error);
    return false;
  }
}

export async function deleteUserAccount(
  supabase: SupabaseClient, 
  fetchFunction: (url: string, options: any) => Promise<any>
): Promise<boolean> {
  try {
    const { data: { user }, error } = await supabase.auth.getUser();
    
    if (error || !user) {
      console.error('No authenticated user found:', error);
      return false;
    }
    
    const response = await fetchFunction('/api/user/delete-account', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ user_id: user.id }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      console.error('Delete account response error:', errorData);
      throw new Error(errorData.message || `Failed to delete account: ${response.status}`);
    }

    await supabase.auth.signOut();
    return true;
  } catch (error) {
    console.error('Error in deleteUserAccount:', error);
    return false;
  }
}

export async function getUserSubscription(supabase: SupabaseClient): Promise<UserSubscription | null> {
  try {
    const { data: { user }, error: userError } = await supabase.auth.getUser();
    if (userError || !user) {
      return null;
    }

    const { data, error } = await supabase
      .rpc('get_user_subscription')
      .single();

    if (error) {
      if (error.code === 'PGRST116') {
        return null;
      }
      console.error('Error fetching subscription data:', error);
      return null;
    }

    return data as UserSubscription;
  } catch (error) {
    console.error('Error in getUserSubscription:', error);
    return null;
  }
}

export async function getUserUsage(supabase: SupabaseClient) {
  try {
    const { data: { user }, error: userError } = await supabase.auth.getUser();
    if (userError || !user) {
      console.log('No authenticated user found');
      return { user_id: 'unknown', api_call_count: 0, active_flow_count: 0, message_count: 0 };
    }

    const { data, error } = await supabase
      .from('user_monthly_usage_view')
      .select('*')
      .eq('user_id', user.id)
      .single();

      

    console.log('User ID:', user.id);
    console.log('Data:', data);
    console.log('Error:', error);

    if (error) {
      if (error.code === 'PGRST116') {
        console.log('No usage records found, returning default values');
        return { user_id: user.id, api_call_count: 0, active_flow_count: 0, message_count: 0 };
      }
      console.error('Error fetching usage data:', error);
      return { user_id: user.id, api_call_count: 0, active_flow_count: 0, message_count: 0 };
    }

    return data;
  } catch (error) {
    console.error('Error in getUserUsage:', error);
    return { user_id: 'unknown', api_call_count: 0, active_flow_count: 0, message_count: 0 };
  }
}

export async function getProductInfoByTag(supabase: SupabaseClient, tag: string) {
  try {
    const { data, error } = await supabase
      .from('products_info')
      .select('*')
      .eq('product_tag', tag)
      .single();

    if (error) {
      console.error('Error fetching product info:', error);
      return null;
    }

    if (data && typeof data.attrs === 'string') {
      data.attrs = JSON.parse(data.attrs);
    }

    return data;
  } catch (error) {
    console.error('Error in getProductInfo:', error);
    return null;
  }
}

export async function getUserProductInfo(supabase: SupabaseClient) {
  try {
    const subscription = await getUserSubscription(supabase);
    
    if (subscription) {
      const productName = subscription.product_name.toLowerCase();
      let productTag = 'free';
      
      if (productName.includes('pro')) {
        productTag = 'pro';
      } else if (productName.includes('team')) {
        productTag = 'teams';
      } else if (productName.includes('starter')) {
        productTag = 'starter';
      }
      
      return await getProductInfoByTag(supabase, productTag);
    } else {
      return await getProductInfoByTag(supabase, 'free');
    }
  } catch (error) {
    console.error('Error getting user product info:', error);
    return await getProductInfoByTag(supabase, 'free');
  }
}

export async function isUserOnFreePlan(supabase: SupabaseClient): Promise<boolean> {
  try {
    const subscription = await getUserSubscription(supabase);
    return !subscription;
  } catch (error) {
    console.error('Error checking if user is on free plan:', error);
    return true;
  }
}

export async function getUserPlanName(supabase: SupabaseClient): Promise<string> {
  try {
    const productInfo = await getUserProductInfo(supabase);
    return productInfo?.product_tag || 'free';
  } catch (error) {
    console.error('Error getting user plan name:', error);
    return 'free';
  }
}

export async function canUserCreateFlow(
  supabase: SupabaseClient,
  increment: number = 1
): Promise<{
  allowed: boolean;
  reason?: string;
  current?: number;
  limit?: number | string;
  needsUpgrade?: boolean;
}> {
  try {
    const [productInfo, usage] = await Promise.all([
      getUserProductInfo(supabase),
      getUserUsage(supabase)
    ]);

    if (!productInfo || !usage) {
      return { 
        allowed: false, 
        reason: 'Could not fetch user plan or usage information',
        needsUpgrade: false
      };
    }

    const currentFlows = usage.active_flow_count || 0;
    const flowLimit = productInfo.attrs?.active_flow_count;
    
    if (typeof flowLimit === 'string') {
      return { 
        allowed: true, 
        current: currentFlows, 
        limit: flowLimit 
      };
    }
    
    const wouldExceed = (currentFlows + increment) > flowLimit;
    
    return {
      allowed: !wouldExceed,
      reason: wouldExceed ? `You have reached the limit of ${flowLimit} flows on your current plan.` : undefined,
      current: currentFlows,
      limit: flowLimit,
      needsUpgrade: wouldExceed
    };
  } catch (error) {
    console.error('Error checking flow creation limit:', error);
    return { allowed: true };
  }
}

export async function canUserCallAPI(
  supabase: SupabaseClient,
  increment: number = 1
): Promise<{
  allowed: boolean;
  reason?: string;
  current?: number;
  limit?: number | string;
  needsUpgrade?: boolean;
}> {
  try {
    const [productInfo, usage] = await Promise.all([
      getUserProductInfo(supabase),
      getUserUsage(supabase)
    ]);

    if (!productInfo || !usage) {
      return { 
        allowed: false, 
        reason: 'Could not fetch user plan or usage information',
        needsUpgrade: false
      };
    }

    const currentCalls = usage.api_call_count || 0;
    const callLimit = productInfo.attrs?.api_call_count;
    
    if (typeof callLimit === 'string') {
      return { 
        allowed: true, 
        current: currentCalls, 
        limit: callLimit 
      };
    }
    
    const wouldExceed = (currentCalls + increment) > callLimit;
    
    return {
      allowed: !wouldExceed,
      reason: wouldExceed ? `You have reached the maximum of ${callLimit} API requests on your current plan` : undefined,
      current: currentCalls,
      limit: callLimit,
      needsUpgrade: wouldExceed
    };
  } catch (error) {
    console.error('Error checking API call limit:', error);
    return { allowed: true };
  }
}

export async function canUserSendMessage(
  supabase: SupabaseClient,
  increment: number = 1
): Promise<{
  allowed: boolean;
  reason?: string;
  current?: number;
  limit?: number | string;
  needsUpgrade?: boolean;
}> {
  try {
    const [productInfo, usage] = await Promise.all([
      getUserProductInfo(supabase),
      getUserUsage(supabase)
    ]);

    if (!productInfo || !usage) {
      return { 
        allowed: false, 
        reason: 'Could not fetch user plan or usage information',
        needsUpgrade: false
      };
    }

    const currentMessages = usage.message_count || 0;
    const messageLimit = productInfo.attrs?.message_count;
    
    if (typeof messageLimit === 'string') {
      return { 
        allowed: true, 
        current: currentMessages, 
        limit: messageLimit 
      };
    }
    
    const atLimit = (currentMessages + increment) > messageLimit;
    
    return {
      allowed: !atLimit,
      reason: atLimit ? `You have reached the maximum of ${messageLimit} messages on your current plan` : undefined,
      current: currentMessages,
      limit: messageLimit,
      needsUpgrade: atLimit
    };
  } catch (error) {
    console.error('Error checking message limit:', error);
    return { allowed: true };
  }
} 