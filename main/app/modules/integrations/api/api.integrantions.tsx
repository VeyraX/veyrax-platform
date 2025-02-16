import { createClient } from '@/lib/utils/supabase/client'
import { IntegrationCardProps, Provider } from './types.integrations'
import { getAuthHeaders } from '@/lib/actions/actions'

export const getIntegrationsData = async (): Promise<IntegrationCardProps[]> => {
  const supabase = createClient()
  
  const { data: { user } } = await supabase.auth.getUser()
  
  const { data: providers } = await supabase
    .from('providers')
    .select('*')

  const { data: userProviders } = await supabase
    .from('users_providers')
    .select('provider_id')
    .eq('user_id', user?.id)

  const { data: userIndexes } = await supabase
    .from('users_provider_indexes')
    .select('provider_id')
    .eq('user_id', user?.id)

  const connectedProviderIds = new Set(userProviders?.map(p => p.provider_id))
  const indexedProviderIds = new Set(userIndexes?.map(index => index.provider_id))

  return providers?.map((provider: Provider) => ({
    ...provider,
    connected: connectedProviderIds.has(provider.id),
    hasIndex: indexedProviderIds.has(provider.id)
  })) || []
}

export const enableProvider = async (providerId: string): Promise<void> => {
  const supabase = createClient()
  const { data: { user } } = await supabase.auth.getUser()

  await supabase
    .from('users_providers')
    .upsert({ 
      user_id: user?.id,
      provider_id: providerId 
    })
}

export const disconnectProvider = async (providerId: string): Promise<void> => {
  const supabase = createClient()
  const { data: { user } } = await supabase.auth.getUser()

  await supabase
    .from('users_providers')
    .delete()
    .match({ 
      user_id: user?.id,
      provider_id: providerId 
    })

  await supabase
    .from('users_oauth_tokens')
    .delete()
    .match({ 
      user_id: user?.id,
      provider_id: providerId 
    })
}

export const deleteProviderIndex = async (providerId: string): Promise<void> => {
  const supabase = createClient()
  const { data: { user } } = await supabase.auth.getUser()

  await supabase
    .from('users_provider_indexes')
    .delete()
    .match({
      user_id: user?.id,
      provider_id: providerId
    })
}

export const createProviderIndex = async (providerId: string, providerTag: string): Promise<void> => {
  const supabase = createClient()
  const { data: { user } } = await supabase.auth.getUser()

  const headers = await getAuthHeaders();
  const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/vector-tools/index-data`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ 
      collection_name: providerTag 
    }),
    credentials: 'include'
  });

  if (!response.ok) {
    throw new Error('Failed to create index');
  }

  await supabase
    .from('users_provider_indexes')
    .upsert({
      user_id: user?.id,
      provider_id: providerId,
      status: 'syncing'
    }, {
      onConflict: 'provider_id,user_id'
    });
}

export const initiateOAuthFlow = async (providerTag: string, scopes: string[]): Promise<string> => {
  const response = await fetch(`/api/oauth/${providerTag}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ scopes })
  });
  
  const { url } = await response.json();
  return url;
}

export const enableApiKeyProvider = async (providerId: string): Promise<void> => {
  const supabase = createClient();
  const { data: { user } } = await supabase.auth.getUser();
  
  const { error } = await supabase
    .from('users_providers')
    .upsert({
      user_id: user?.id,
      provider_id: providerId
    }, {
      onConflict: 'provider_id,user_id'
    });

  if (error) throw error;
}