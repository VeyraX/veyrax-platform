import { createClient } from '@/lib/utils/supabase/client'
import { IntegrationCardProps, Provider } from './types.integrations'

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