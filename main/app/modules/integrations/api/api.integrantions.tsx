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
    .select('provider_id, status, collection_name, last_sync_date')
    .eq('user_id', user?.id)

  const connectedProviderIds = new Set(userProviders?.map(p => p.provider_id))
  const indexStatusMap = new Map(
    userIndexes?.map(index => [index.provider_id, index.status])
  )
  const lastSyncDateMap = new Map(
    userIndexes?.map(index => [index.provider_id, index.last_sync_date])
  )

  console.log(userIndexes)

  return providers?.map((provider: Provider) => ({
    ...provider,
    connected: connectedProviderIds.has(provider.id),
    hasIndex: indexStatusMap.has(provider.id),
    indexStatus: indexStatusMap.get(provider.id),
    lastSyncDate: lastSyncDateMap.get(provider.id)
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

  await supabase
    .from('users_provider_indexes')
    .upsert({
      user_id: user?.id,
      provider_id: providerId,
      collection_name: providerTag,
      status: 'syncing'
    }, {
      onConflict: 'user_id,provider_id'
    })
    .then(({ data, error }) => {
      if (error) {
        console.error('Index creation error:', error);
        throw error;
      }
      console.log('Index upsert result:', { data, error });
    });

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
    await supabase
      .from('users_provider_indexes')
      .upsert({
        user_id: user?.id,
        provider_id: providerId,
        status: 'failed'
      }, {
        onConflict: 'user_id,provider_id'
      });
    throw new Error('Failed to create index');
  }

  console.log('Starting index creation for provider:', providerId);
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

export const checkIndexStatus = async (providerId: string): Promise<string | null> => {
  const supabase = createClient();
  const { data: { user } } = await supabase.auth.getUser();
  
  const { data } = await supabase
    .from('users_provider_indexes')
    .select('status')
    .match({ 
      user_id: user?.id,
      provider_id: providerId 
    })
    .single();
  
  return data?.status || null;
};