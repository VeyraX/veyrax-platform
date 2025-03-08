import { createClient } from '@/lib/utils/supabase/client'
import { IntegrationCardProps, Provider, ProviderDetails, ProviderEndpoint, DbConfig, UserDbAccess } from './types.integrations'

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

  const connectedProviderIds = new Set(userProviders?.map(p => p.provider_id))

  const { data: userApiKeys } = await supabase
    .from('users_provider_api_keys')
    .select('provider_id, api_key')
    .eq('user_id', user?.id)

  const providersWithApiKeys = new Set(
    userApiKeys
      ?.filter(k => k.api_key && k.api_key.trim() !== '')
      .map(k => k.provider_id)
  )

  const result = providers?.map((provider: Provider) => {
    const isConnected = connectedProviderIds.has(provider.id);
    
    const isReallyConnected = provider.auth_method === 'api_key' 
      ? providersWithApiKeys.has(provider.id) 
      : isConnected;

    return {
      ...provider,
      connected: isReallyConnected,
      hasIndex: false,
      indexStatus: null,
      lastSyncDate: null,
      processedEntities: null
    };
  }) || []
  
  return result as IntegrationCardProps[]
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

export const enableDbAccessProvider = async (providerId: string, dbConfig: DbConfig): Promise<void> => {
  const { data: { user } } = await supabase.auth.getUser();
  
  const { data: provider } = await supabase
    .from('providers')
    .select('provider_tag')
    .eq('id', providerId)
    .single();
  
  const isSnowflake = provider?.provider_tag === 'snowflake';
  
  if (isSnowflake) {
    if (!dbConfig.account || !dbConfig.user || !dbConfig.password || !dbConfig.database) {
      await disconnectProvider(providerId);
      return;
    }
  } else {
    if (!dbConfig.host || !dbConfig.port || !dbConfig.dbname || !dbConfig.user || !dbConfig.password) {
      await disconnectProvider(providerId);
      return;
    }
  }
  
  const { error: providerError } = await supabase
    .from('users_providers')
    .upsert({
      user_id: user?.id,
      provider_id: providerId
    }, {
      onConflict: 'provider_id,user_id'
    });

  if (providerError) throw providerError;
  
  const response = await fetch('/api/encrypt', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ apiKey: dbConfig.password })
  });
  
  if (!response.ok) {
    throw new Error('Failed to encrypt database password');
  }
  
  const { encryptedKey } = await response.json();
  
  const credentials = {
    ...dbConfig,
    password: encryptedKey
  };
  
  const { data: existingCredentials } = await supabase
    .from('users_db_access')
    .select('id')
    .eq('user_id', user?.id)
    .eq('provider_id', providerId)
    .single();
  
  let dbAccessError;
  
  if (existingCredentials) {
    const { error } = await supabase
      .from('users_db_access')
      .update({ credentials: JSON.stringify(credentials) })
      .eq('id', existingCredentials.id);
    
    dbAccessError = error;
  } else {
    const { error } = await supabase
      .from('users_db_access')
      .insert({
        user_id: user?.id,
        provider_id: providerId,
        credentials: JSON.stringify(credentials)
      });
    
    dbAccessError = error;
  }

  if (dbAccessError) throw dbAccessError;
}

export const getUserDbCredentials = async (providerId: string): Promise<DbConfig | null> => {
  const { data: { user } } = await supabase.auth.getUser();
  
  const { data, error } = await supabase
    .from('users_db_access')
    .select('credentials')
    .eq('user_id', user?.id)
    .eq('provider_id', providerId)
    .single();
  
  if (error || !data) return null;
  
  try {
    const credentials = JSON.parse(data.credentials) as DbConfig;
    
    return credentials;
  } catch (error) {
    console.error('Error parsing credentials:', error);
    return null;
  }
}

export const disconnectProvider = async (providerId: string): Promise<void> => {
  const { data: { user } } = await supabase.auth.getUser()

  await supabase
    .from('users_provider_api_keys')
    .delete()
    .match({ 
      user_id: user?.id,
      provider_id: providerId 
    });

  await supabase
    .from('users_db_access')
    .delete()
    .match({ 
      user_id: user?.id,
      provider_id: providerId 
    });

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

export const enableApiKeyProvider = async (providerId: string, apiKey: string): Promise<void> => {
  const { data: { user } } = await supabase.auth.getUser();
  
  if (!apiKey) {
    await disconnectProvider(providerId);
    return;
  }
  
  const { error: providerError } = await supabase
    .from('users_providers')
    .upsert({
      user_id: user?.id,
      provider_id: providerId
    }, {
      onConflict: 'provider_id,user_id'
    });

  if (providerError) throw providerError;
  
  const response = await fetch('/api/encrypt', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ apiKey })
  });
  
  if (!response.ok) {
    throw new Error('Failed to encrypt API key');
  }
  
  const { encryptedKey } = await response.json();
  
  const { data: existingKey } = await supabase
    .from('users_provider_api_keys')
    .select('id')
    .eq('user_id', user?.id)
    .eq('provider_id', providerId)
    .single();
  
  let apiKeyError;
  
  if (existingKey) {
    const { error } = await supabase
      .from('users_provider_api_keys')
      .update({ api_key: encryptedKey })
      .eq('id', existingKey.id);
    
    apiKeyError = error;
  } else {
    const { error } = await supabase
      .from('users_provider_api_keys')
      .insert({
        user_id: user?.id,
        provider_id: providerId,
        api_key: encryptedKey
      });
    
    apiKeyError = error;
  }

  if (apiKeyError) throw apiKeyError;
}

export const getUserApiKey = async (providerId: string): Promise<string | null> => {
  const { data: { user } } = await supabase.auth.getUser();
  
  const { data, error } = await supabase
    .from('users_provider_api_keys')
    .select('api_key')
    .eq('user_id', user?.id)
    .eq('provider_id', providerId)
    .single();
  
  if (error || !data) return null;
  return data.api_key;
}

export const getUserConnectedTools = async (): Promise<{ providerTag: string, logoUrl: string, isConnected: boolean }[]> => {
  const { data: { user } } = await supabase.auth.getUser()
  
  type ProviderResponse = {
    providers: {
      provider_tag: string,
      logo_url: string,
      auth_method: string,
      id: string
    }
  }
  
  const { data: userProviders } = await supabase
    .from('users_providers')
    .select('providers(provider_tag, logo_url, auth_method, id)')
    .eq('user_id', user?.id) as { data: ProviderResponse[] | null }
  
  if (!userProviders?.length) return [];
  
  const { data: userApiKeys } = await supabase
    .from('users_provider_api_keys')
    .select('provider_id, api_key')
    .eq('user_id', user?.id)

  const providersWithApiKeys = new Set(
    userApiKeys
      ?.filter(k => k.api_key && k.api_key.trim() !== '')
      .map(k => k.provider_id)
  )
  
  return userProviders.map(up => {
    const isApiKeyProvider = up.providers.auth_method === 'api_key';
    const isReallyConnected = isApiKeyProvider 
      ? providersWithApiKeys.has(up.providers.id) 
      : true;
      
    return {
      providerTag: up.providers.provider_tag,
      logoUrl: up.providers.logo_url,
      isConnected: isReallyConnected
    };
  }) || [];
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
  let exampleSchema = {};
  
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

  try {
    exampleSchema = typeof provider.example_schema === 'string'
      ? JSON.parse(provider.example_schema)
      : provider.example_schema || {};
  } catch (e) {
    console.error('Error parsing example schema:', e);
    exampleSchema = {};
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

  endpointsList.sort((a, b) => {
    const getKeyParts = (name: string) => {
      const parts = name.split('_');
      const action = parts[0] || '';
      const entity = parts.slice(1).join('_') || '';
      return { action, entity };
    };

    const partsA = getKeyParts(a.name);
    const partsB = getKeyParts(b.name);

    if (partsA.entity !== partsB.entity) {
      return partsA.entity.localeCompare(partsB.entity);
    }
    
    return partsA.action.localeCompare(partsB.action);
  });

  return {
    provider,
    totalEndpoints,
    totalParameters,
    totalComponents,
    endpointsList,
    exampleSchema
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
  
  return componentWithRelatedEndpoint || null;
};

export const testDbConnection = async (providerId: string, dbConfig: DbConfig): Promise<{success: boolean, message: string}> => {
  try {
    const { data: provider, error: providerError } = await supabase
      .from('providers')
      .select('provider_tag')
      .eq('id', providerId)
      .single();
    
    if (providerError) throw providerError;
    
    const providerTag = provider.provider_tag;
    
    const response = await fetch(`/api/integrations/test_connection`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        providerTag,
        dbConfig
      })
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      return { 
        success: false, 
        message: errorData.message || 'Connection test failed' 
      };
    }
    
    const result = await response.json();
    return result.data;
  } catch (error) {
    console.error('Error testing database connection:', error);
    return { 
      success: false, 
      message: error instanceof Error ? error.message : 'Unknown error occurred' 
    };
  }
};

export const getUserMemoryChunks = async (): Promise<any[]> => {
  const { data: { user } } = await supabase.auth.getUser()
  try {
    const { data, error } = await supabase
      .from('users_memory')
      .select('*')
      .eq('user_id', user?.id);
    
    if (error) throw error;
    console.log(data);
    
    return data || [];
  } catch (error) {
    console.error('Error fetching memory chunks:', error);
    throw error;
  }
};

export const deleteUserMemoryChunk = async (chunkId: string): Promise<void> => {
  const { data: { user } } = await supabase.auth.getUser()
  try {
    const { error } = await supabase
      .from('users_memory')
      .delete()
      .eq('id', chunkId)
      .eq('user_id', user?.id);
    
    if (error) throw error;
  } catch (error) {
    console.error('Error deleting memory chunk:', error);
    throw error;
  }
};

export const upsertIntegrationRequest = async (integrationName: string): Promise<void> => {
  const { data: { user } } = await supabase.auth.getUser();
  
  if (!user?.id) {
    throw new Error('User not authenticated');
  }
  
  try {
    const { error } = await supabase
      .from('integration_requests')
      .upsert({
        user_id: user.id,
        integration_name: integrationName,
        created_at: new Date().toISOString()
      });
    
    if (error) throw error;
  } catch (error) {
    console.error('Error upserting integration request:', error);
    throw error;
  }
};