import { createClient } from '@/lib/utils/supabase/client'
import { IntegrationCardProps, Provider, ProviderDetails, ProviderEndpoint } from './types.integrations'
import { getAuthHeaders } from '@/lib/actions/actions'

const supabase = createClient()


export const getIntegrationsData = async (): Promise<IntegrationCardProps[]> => {
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
    .select('provider_id, status, collection_name, last_sync_date, processed_entities')
    .eq('user_id', user?.id)

  const connectedProviderIds = new Set(userProviders?.map(p => p.provider_id))
  const indexStatusMap = new Map(
    userIndexes?.map(index => [index.provider_id, index.status])
  )
  const lastSyncDateMap = new Map(
    userIndexes?.map(index => [index.provider_id, index.last_sync_date])
  )
  const processedEntitiesMap = new Map(
    userIndexes?.map(index => [index.provider_id, index.processed_entities])
  )


  const result = providers?.map((provider: Provider) => ({
    ...provider,
    connected: connectedProviderIds.has(provider.id),
    hasIndex: indexStatusMap.has(provider.id),
    indexStatus: indexStatusMap.get(provider.id),
    lastSyncDate: lastSyncDateMap.get(provider.id),
    processedEntities: processedEntitiesMap.get(provider.id)
  })) || []
  
  return result
}

export const enableProvider = async (providerId: string): Promise<void> => {
  const { data: { user } } = await supabase.auth.getUser()

  await supabase
    .from('users_providers')
    .upsert({ 
      user_id: user?.id,
      provider_id: providerId 
    })
}

export const disconnectProvider = async (providerId: string): Promise<void> => {
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

export const createProviderIndex = async (providerId: string, providerTag: string): Promise<void> => {
  const { data: { user } } = await supabase.auth.getUser()

  await supabase
    .from('users_provider_indexes')
    .upsert({
      user_id: user?.id,
      provider_id: providerId,
      collection_name: providerTag,
      status: 'pending'
    }, {
      onConflict: 'user_id,provider_id'
    })
    .then(({ data, error }) => {
      if (error) {
        console.error('Index creation error:', error);
        throw error;
      }
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

export const deleteIndexData = async (providerTag: string): Promise<void> => {
  const headers = await getAuthHeaders();
  const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/vector-tools/delete-index-data`, {
    method: 'DELETE',
    headers,
    body: JSON.stringify({ 
      collection_name: providerTag 
    }),
    credentials: 'include'
  });

  if (!response.ok) {
    throw new Error('Failed to delete index data');
  }
}

export const getUserConnectedTools = async (): Promise<{ providerTag: string, logoUrl: string }[]> => {
  const { data: { user } } = await supabase.auth.getUser()
  
  type ProviderResponse = {
    providers: {
      provider_tag: string,
      logo_url: string
    }
  }
  
  const { data: userProviders } = await supabase
    .from('users_providers')
    .select('providers(provider_tag, logo_url)')
    .eq('user_id', user?.id) as { data: ProviderResponse[] | null }
  
  return userProviders?.map(up => ({
    providerTag: up.providers.provider_tag,
    logoUrl: up.providers.logo_url
  })) || []
}

export const getProviderDetails = async (providerTag: string): Promise<ProviderDetails> => {
  const { data: provider, error } = await supabase
    .from('providers')
    .select('*')
    .eq('provider_tag', providerTag)
    .single();

  if (error) {
    console.error('Error fetching provider details:', error);
    throw error;
  }

  let inputSchema = {};
  let uiComponents = [];
  
  try {
    inputSchema = typeof provider.input_schema === 'string' 
      ? JSON.parse(provider.input_schema) 
      : provider.input_schema || {};
  } catch (e) {
    console.error('Error parsing input schema:', e);
  }
  
  try {
    uiComponents = typeof provider.ui_component === 'string' 
      ? JSON.parse(provider.ui_component) 
      : provider.ui_component || [];
    
    if (!Array.isArray(uiComponents)) {
      uiComponents = [uiComponents].filter(Boolean);
    }
  } catch (e) {
    console.error('Error parsing UI components:', e);
    uiComponents = [];
  }

  const totalEndpoints = Object.keys(inputSchema).length;

  let totalParameters = 0;
  Object.values(inputSchema).forEach((endpoint: any) => {
    if (endpoint?.function?.parameters?.properties) {
      const topLevelParams = Object.keys(endpoint.function.parameters.properties).length;
      
      let nestedParams = 0;
      Object.entries(endpoint.function.parameters.properties).forEach(([_, propValue]: [string, any]) => {
        if (propValue.$ref && endpoint.function.parameters.$defs) {
          const defName = propValue.$ref.split('/').pop();
          const definition = endpoint.function.parameters.$defs[defName];
          
          if (definition?.properties) {
            nestedParams += Object.keys(definition.properties).length;
          }
        }
      });
      
      totalParameters += topLevelParams + nestedParams;
    }
  });

  const totalComponents = uiComponents.length;

  const endpointsList: ProviderEndpoint[] = Object.entries(inputSchema).map(([key, value]: [string, any]) => {
    const functionName = value?.function?.name || key;
    const description = value?.function?.description || '';
    
    let paramCount = 0;
    if (value?.function?.parameters?.properties) {
      paramCount = Object.keys(value.function.parameters.properties).length;
      
      Object.entries(value.function.parameters.properties).forEach(([_, propValue]: [string, any]) => {
        if (propValue.$ref && value.function.parameters.$defs) {
          const defName = propValue.$ref.split('/').pop();
          const definition = value.function.parameters.$defs[defName];
          
          if (definition?.properties) {
            paramCount += Object.keys(definition.properties).length;
          }
        }
      });
    }
    
    return {
      name: key,
      functionId: functionName,
      description,
      paramCount
    };
  });

  return {
    provider,
    totalEndpoints,
    totalParameters,
    totalComponents,
    endpointsList
  };
};

export const findComponentForEndpoint = async (providerTag: string, endpointName: string): Promise<any> => {
  const { data: provider, error } = await supabase
    .from('providers')
    .select('ui_component')
    .eq('provider_tag', providerTag)
    .single();

  if (error) {
    console.error('Error fetching provider components:', error);
    throw error;
  }

  let uiComponents = [];
  try {
    uiComponents = typeof provider.ui_component === 'string' 
      ? JSON.parse(provider.ui_component) 
      : provider.ui_component || [];
    
    if (!Array.isArray(uiComponents)) {
      uiComponents = [uiComponents].filter(Boolean);
    }
  } catch (e) {
    console.error('Error parsing UI components:', e);
    return null;
  }

  const componentWithRelatedEndpoint = uiComponents.find(component => 
    component.related_endpoints && 
    component.related_endpoints.includes(endpointName)
  );
  
  if (componentWithRelatedEndpoint) {
    return componentWithRelatedEndpoint;
  }
  
  return uiComponents.length > 0 ? uiComponents[0] : null;
};