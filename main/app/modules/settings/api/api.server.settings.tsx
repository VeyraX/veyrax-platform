import { createClient } from '@/lib/utils/supabase/server';
import * as CoreApi from './api.core.settings';
import { fetch } from 'next/dist/compiled/@edge-runtime/primitives';
import { createClient as createServiceClient } from '@supabase/supabase-js';
import { ModelId, AI_MODELS, DEFAULT_MODEL, initializeModel } from '@/app/modules/agent/components/api/models';
import { decrypt } from '@/lib/utils/encryption';

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

export async function getUserPlaygroundSettingsServer() {
  return CoreApi.getUserPlaygroundSettings(createClient());
}

export async function getUserModelServer() {
  const client = createClient();
  
  try {
    const { data: { user } } = await client.auth.getUser();
    
    if (user) {
      const { data: settings } = await client
        .from('user_playground_settings')
        .select('ai_model, api_key_enabled, api_key_provider_name, api_key')
        .eq('user_id', user.id)
        .single();
      
      if (settings?.ai_model) {
        if (settings.api_key_enabled && settings.api_key && settings.api_key.includes(':')) {
          try {
            settings.api_key = decrypt(settings.api_key);
          } catch (error) {
            console.error('Error decrypting API key:', error);
          }
        }
        
        const supabase = createClient();
        const { models: availableModels } = await CoreApi.getUserAvailableModels(
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

        console.log('settings.ai_model', settings.ai_model);
        
        const modelDetails = AI_MODELS[settings.ai_model as ModelId];
        throw {
          code: "PREMIUM_MODEL_ACCESS_REQUIRED",
          message: "Premium model access required",
          modelId: settings.ai_model,
          modelName: modelDetails?.name || settings.ai_model
        };
      }
    }

    console.log('DEFAULT_MODEL', DEFAULT_MODEL);
    
    return initializeModel(DEFAULT_MODEL);
  } catch (error) {
    if (error && typeof error === 'object' && 'code' in error) {
      throw error;
    }
    
    console.error('Error in getUserModelServer:', error);
    return initializeModel(DEFAULT_MODEL);
  }
}

export async function getUserAgentPromptServer() {
  return CoreApi.getUserAgentPrompt(createClient());
}

export async function canUserRentKeyServer(userId: string) {
  try {
    const client = createServiceClient(
      process.env.SUPABASE_URL!,
      process.env.SUPABASE_SERVICE_KEY!
    );

    const { data: subscription } = await client
      .from('users_subscription_status_view')
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