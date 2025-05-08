'use client';

import { createClient } from '@/lib/utils/supabase/client';
import { UserProfile, UserApiKey, UserSubscription } from './types.settings'
import * as CoreApi from './api.core.settings'
import { ModelId, initializeModel, DEFAULT_MODEL } from '@/app/modules/agent/components/api/models';

export async function getUserProfile(): Promise<UserProfile | null> {
  return CoreApi.getUserProfile(createClient())
}

export async function getUserApiKey(): Promise<UserApiKey | null> {
  return CoreApi.getUserApiKey(createClient())
}

export async function generateApiKey(): Promise<UserApiKey | null> {
  return CoreApi.generateApiKey(createClient(), () => {
    const randomBytes = new Uint8Array(20)
    window.crypto.getRandomValues(randomBytes)
    return randomBytes
  })
}

export async function revokeApiKey(): Promise<boolean> {
  return CoreApi.revokeApiKey(createClient())
}

export async function deleteUserAccount(): Promise<boolean> {
  return CoreApi.deleteUserAccount(createClient(), fetch)
}

export async function getUserSubscription() {
  return CoreApi.getUserSubscription(createClient())
}

export async function getUserUsage() {
  return CoreApi.getUserUsage(createClient())
}

export async function getUserProductInfo() {
  return CoreApi.getUserProductInfo(createClient())
}

export async function isUserOnFreePlan() {
  return CoreApi.isUserOnFreePlan(createClient())
}
export async function canUserCreateFlow(increment: number = 1) {
  return CoreApi.canUserCreateFlow(createClient(), increment)
}

export async function canUserCallAPI(increment: number = 1) {
  return CoreApi.canUserCallAPI(createClient(), increment)
}

export async function canUserSendMessage(increment: number = 1) {
  return CoreApi.canUserSendMessage(createClient(), increment)
}

export async function canUserRentKey() {
  return CoreApi.canUserRentKey(createClient())
}

export async function getUserPlaygroundSettings() {
  return CoreApi.getUserPlaygroundSettings(createClient())
}

export async function saveUserPlaygroundSettings(settings: {
  agent_prompt: string;
  ai_model: string;
  api_key_provider_name: string;
  api_key: string;
  api_key_enabled: boolean;
}) {
  if (settings.api_key_enabled && settings.api_key) {
    if (!settings.api_key.includes(':')) {
      try {
        const response = await fetch('/api/encrypt', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ apiKey: settings.api_key })
        });
        
        if (response.ok) {
          const { encryptedKey } = await response.json();
          return CoreApi.saveUserPlaygroundSettings(createClient(), {
            ...settings,
            api_key: encryptedKey
          });
        } else {
          console.error('Failed to encrypt API key');
        }
      } catch (error) {
        console.error('Error encrypting API key:', error);
      }
    }
  }
  
  return CoreApi.saveUserPlaygroundSettings(createClient(), settings);
}

export async function getUserAvailableModels(
  userApiKeySettings?: {
    api_key_enabled: boolean;
    api_key_provider_name: string;
  }
) {
  return CoreApi.getUserAvailableModels(createClient(), userApiKeySettings);
}

export async function validateApiKey(
  provider: string,
  apiKey: string
) {
  return CoreApi.validateApiKey(provider, apiKey);
}

export async function getUserModel() {
  return CoreApi.getUserModelCore(createClient());
}