import { createClient } from '@/lib/utils/supabase/client'
import { IntegrationCardProps, Provider } from './types.integrations'

export const getIntegrationsData = async (): Promise<IntegrationCardProps[]> => {
  const supabase = createClient()
  
  const { data: { user } } = await supabase.auth.getUser()
  const { data: { session } } = await supabase.auth.getSession()
  
  const { data: providers } = await supabase
    .from('providers')
    .select('*')


  const { data: userTokens } = await supabase
    .from('users_oauth_tokens')
    .select('provider_id')
    .eq('user_id', user?.id)

  const connectedProviderIds = new Set(userTokens?.map(token => token.provider_id))

  return providers?.map((provider: Provider) => ({
    ...provider,
    connected: connectedProviderIds.has(provider.id)
  })) || []
}

export const disconnectProvider = async (providerId: string): Promise<void> => {
  const supabase = createClient()
  const { data: { user } } = await supabase.auth.getUser()

  await supabase
    .from('users_oauth_tokens')
    .delete()
    .match({ 
      user_id: user?.id,
      provider_id: providerId 
    })
}