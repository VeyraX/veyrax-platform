import { SupabaseClient } from '@supabase/supabase-js';
import { UserProfile, UserApiKey, UserSubscription, UserAvailableModels } from './types.settings';
import { AI_MODELS, ModelId, initializeModel, DEFAULT_MODEL } from '../../agent/components/api/models';

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

export async function getUserRegistrationDate(supabase: SupabaseClient): Promise<string | null> {
  try {
    const { data: { user }, error: userError } = await supabase.auth.getUser();
    if (userError || !user) {
      return null;
    }
    const { data, error } = await supabase
      .rpc('get_current_user_meta');

    if (error) {
      console.error('Error fetching registration date:', error);
      return null;
    }
    return data[0].created_at;
  } catch (error) {
    console.error('Error in getUserRegistrationDate:', error);
    return null;
  }
}

async function isEarlyAdopter(supabase: SupabaseClient): Promise<boolean> {
  try {
    const registrationDate = await getUserRegistrationDate(supabase);
    if (!registrationDate) return false;

    const regDate = new Date(registrationDate);
    const cutoffDate = new Date('2025-04-08T00:00:00Z');
    
    return regDate.getTime() < cutoffDate.getTime();
  } catch (error) {
    console.error('Error checking early adopter status:', error);
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
      // Silently handle all errors including 406 Not Acceptable
      return null;
    }

    return data as UserSubscription;
  } catch (error) {
    // Silently catch any errors
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

export async function getUserProductInfo(supabase: SupabaseClient) {
  try {
    const subscription = await getUserSubscription(supabase);
    
    if (!subscription || subscription.subscription_status !== 'active') {
      const { data, error } = await supabase
        .from('products_info')
        .select('*')
        .eq('product_tag', 'free')
        .single();

      if (error || !data) {
        console.error('Error getting free product info:', error);
        return null;
      }
      return data;
    }

    const { data, error } = await supabase
      .from('products_info')
      .select('*')
      .eq('stripe_product_id', subscription.product_id)
      .single();

    if (error || !data) {
      console.error('Error getting product info:', error);
      return null;
    }

    return data;
  } catch (error) {
    console.error('Error getting user product info:', error);
    return null;
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
    const earlyAdopter = await isEarlyAdopter(supabase);
    if (earlyAdopter) {
      return { 
        allowed: true,
        current: 0,
        limit: "Unlimited for early adopters"
      };
    }

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
    const earlyAdopter = await isEarlyAdopter(supabase);
    if (earlyAdopter) {
      return { 
        allowed: true,
        current: 0,
        limit: "Unlimited for early adopters"
      };
    }

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
    const earlyAdopter = await isEarlyAdopter(supabase);
    if (earlyAdopter) {
      return { 
        allowed: true,
        current: 0,
        limit: "Unlimited for early adopters"
      };
    }

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

export async function canUserRentKey(
  supabase: SupabaseClient
): Promise<{
  allowed: boolean;
  reason?: string;
}> {
  try {
    const productInfo = await getUserProductInfo(supabase);
    if (!productInfo) {
      return { allowed: false, reason: 'Unable to determine user plan' };
    }

    const canRent = productInfo.attrs.rent_provider_keys || false;
    
    return {
      allowed: canRent,
      reason: canRent ? undefined : 'Your current plan does not include this feature'
    };
  } catch (error) {
    console.error('Error checking if user can rent key:', error);
    return { allowed: false, reason: 'An error occurred checking your subscription' };
  }
}

export async function getUserPlaygroundSettings(supabase: SupabaseClient) {
  try {
    const { data: { user }, error: userError } = await supabase.auth.getUser();
    if (userError || !user) {
      return null;
    }

    const { data, error } = await supabase
      .from('user_playground_settings')
      .select('*')
      .eq('user_id', user.id)
      .single();

    if (error) {
      if (error.code === 'PGRST116') {
        return null;
      }
      console.error('Error fetching playground settings:', error);
      return null;
    }

    return data;
  } catch (error) {
    console.error('Error in getUserPlaygroundSettings:', error);
    return null;
  }
}

export async function saveUserPlaygroundSettings(
  supabase: SupabaseClient,
  settings: {
    agent_prompt: string;
    ai_model: string;
    api_key_provider_name: string;
    api_key: string;
    api_key_enabled: boolean;
  }
) {
  try {
    const { data: { user }, error: userError } = await supabase.auth.getUser();
    if (userError || !user) {
      return null;
    }

    const { data: existingSettings } = await supabase
      .from('user_playground_settings')
      .select('id')
      .eq('user_id', user.id)
      .single();

    let result;
    
    if (existingSettings) {
      const { data, error } = await supabase
        .from('user_playground_settings')
        .update({
          agent_prompt: settings.agent_prompt,
          ai_model: settings.ai_model,
          api_key_provider_name: settings.api_key_provider_name,
          api_key: settings.api_key,
          api_key_enabled: settings.api_key_enabled
        })
        .eq('id', existingSettings.id)
        .select()
        .single();
        
      if (error) throw error;
      result = data;
    } else {
      const { data, error } = await supabase
        .from('user_playground_settings')
        .insert({
          user_id: user.id,
          agent_prompt: settings.agent_prompt,
          ai_model: settings.ai_model,
          api_key_provider_name: settings.api_key_provider_name,
          api_key: settings.api_key,
          api_key_enabled: settings.api_key_enabled
        })
        .select()
        .single();
        
      if (error) throw error;
      result = data;
    }

    return result;
  } catch (error) {
    console.error('Error saving playground settings:', error);
    return null;
  }
}

export async function getUserAvailableModels(
  supabase: SupabaseClient,
  userApiKeySettings?: {
    api_key_enabled: boolean;
    api_key_provider_name: string;
  }
): Promise<UserAvailableModels> {
  try {
    const freeModels = Object.entries(AI_MODELS)
      .filter(([_, model]) => !model.isPremium)
      .map(([id]) => id as ModelId);
    
    let availableModels = [...freeModels];
    let isPremiumAllowed = false;

    const productInfo = await getUserProductInfo(supabase);
    if (productInfo?.attrs?.premium_models) {
      isPremiumAllowed = true;
      availableModels = Object.keys(AI_MODELS) as ModelId[];
    }

    if (userApiKeySettings?.api_key_enabled) {
      const providerName = userApiKeySettings.api_key_provider_name;
      
      const providerPremiumModels = Object.entries(AI_MODELS)
        .filter(([_, model]) => 
          model.isPremium && model.originalProvider === providerName
        )
        .map(([id]) => id as ModelId);
      
      providerPremiumModels.forEach(modelId => {
        if (!availableModels.includes(modelId)) {
          availableModels.push(modelId);
        }
      });
    }

    return {
      models: availableModels,
      isPremiumAllowed
    };
  } catch (error) {
    console.error('Error determining available models:', error);
    const freeModels = Object.entries(AI_MODELS)
      .filter(([_, model]) => !model.isPremium)
      .map(([id]) => id as ModelId);
    
    return {
      models: freeModels,
      isPremiumAllowed: false
    };
  }
}

export async function validateApiKey(
  provider: string, 
  apiKey: string
): Promise<{ valid: boolean; error?: string }> {
  try {
    if (provider === 'openai') {
      return await validateOpenAIApiKey(apiKey);
    } else if (provider === 'anthropic') {
      return await validateAnthropicApiKey(apiKey);
    } else {
      return { valid: false, error: `Unsupported provider: ${provider}` };
    }
  } catch (error) {
    console.error(`Error validating ${provider} API key:`, error);
    return { valid: false, error: 'An unexpected error occurred during validation' };
  }
}

export async function getUserModelCore(supabase: SupabaseClient) {
  try {
    const { data: { user } } = await supabase.auth.getUser();
    
    if (user) {
      const { data: settings } = await supabase
        .from('user_playground_settings')
        .select('ai_model, api_key_enabled, api_key_provider_name, api_key')
        .eq('user_id', user.id)
        .single();
      
      if (settings?.ai_model) {
        const { models: availableModels } = await getUserAvailableModels(
          supabase,
          settings.api_key_enabled ? {
            api_key_enabled: settings.api_key_enabled,
            api_key_provider_name: settings.api_key_provider_name
          } : undefined
        );
        
        if (availableModels.includes(settings.ai_model)) {
          return initializeModel(settings.ai_model as ModelId, {
            api_key_enabled: settings.api_key_enabled,
            api_key_provider_name: settings.api_key_provider_name,
            api_key: settings.api_key
          });
        }
        
        const modelDetails = AI_MODELS[settings.ai_model as ModelId];
        throw {
          code: "PREMIUM_MODEL_ACCESS_REQUIRED",
          message: "Premium model access required",
          modelId: settings.ai_model,
          modelName: modelDetails?.name || settings.ai_model
        };
      }
    }
    
    return initializeModel(DEFAULT_MODEL);
  } catch (error) {
    if (error && typeof error === 'object' && 'code' in error) {
      throw error;
    }
    
    console.error('Error in getUserModelCore:', error);
    return initializeModel(DEFAULT_MODEL);
  }
}

async function validateOpenAIApiKey(apiKey: string): Promise<{ valid: boolean; error?: string }> {
  try {
    const response = await fetch('/api/validate-openai-key', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ apiKey })
    });

    if (response.ok) {
      return { valid: true };
    } else {
      const error = await response.json().catch(() => ({}));
      return { 
        valid: false, 
        error: error.error?.message || `Invalid OpenAI API key (Status: ${response.status})` 
      };
    }
  } catch (error) {
    console.error('Error validating OpenAI API key:', error);
    return { valid: false, error: 'Network error during OpenAI validation' };
  }
}

async function validateAnthropicApiKey(apiKey: string): Promise<{ valid: boolean; error?: string }> {
  try {
    const response = await fetch('/api/validate-anthropic-key', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ apiKey })
    });

    if (response.ok) {
      return { valid: true };
    } else {
      const error = await response.json().catch(() => ({}));
      return { 
        valid: false, 
        error: error.error?.message || `Invalid Anthropic API key (Status: ${response.status})` 
      };
    }
  } catch (error) {
    console.error('Error validating Anthropic API key:', error);
    return { valid: false, error: 'Network error during Anthropic validation' };
  }
}

export async function getUserAgentPrompt(supabase: SupabaseClient): Promise<string | null> {
  try {
    const { data: { user }, error: userError } = await supabase.auth.getUser();
    if (userError || !user) {
      return null;
    }

    const { data, error } = await supabase
      .from('user_playground_settings')
      .select('agent_prompt')
      .eq('user_id', user.id)
      .single();

    if (error) {
      if (error.code === 'PGRST116') {
        // Record not found
        return null;
      }
      console.error('Error fetching agent prompt:', error);
      return null;
    }

    return data?.agent_prompt || null;
  } catch (error) {
    console.error('Error in getUserAgentPrompt:', error);
    return null;
  }
} 