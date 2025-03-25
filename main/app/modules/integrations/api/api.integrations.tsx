import { createClient } from '@/lib/utils/supabase/client'
import { IntegrationCardProps, Provider, ProviderDetails, ProviderEndpoint, DbConfig, UserDbAccess } from './types.integrations'

const supabase = createClient()


export const getIntegrationsData = async (): Promise<IntegrationCardProps[]> => {
  const { data: { user } } = await supabase.auth.getUser()
  
  const { data: providers } = await supabase
    .from('providers')
    .select(`
      *,
      provider_scopes (
        scope_id,
        scope_name
      )
    `)

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
  
  const { data: popularProviders } = await supabase
    .from('popular_providers_view')
    .select('*')
  
  const popularProviderIds = new Set(popularProviders?.map(p => p.provider_id) || [])

  const result = providers?.map((provider: Provider & { provider_scopes: Array<{ scope_id: string, scope_name: string }> }) => {
    const isConnected = connectedProviderIds.has(provider.id)
    
    const isReallyConnected = provider.auth_method === 'api_key' 
      ? providersWithApiKeys.has(provider.id) 
      : isConnected
    
    const isPopular = popularProviderIds.has(provider.id)

    return {
      ...provider,
      scopes: provider.provider_scopes?.map(s => ({
        scope: s.scope_id,
        scope_name: s.scope_name
      })) || [],
      connected: isReallyConnected,
      isPopular,
      hasIndex: false,
      indexStatus: null,
      lastSyncDate: null,
      processedEntities: null
    }
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

    console.log('Adding actions user for providerId:', providerId);

    await addActionsUser(providerId);
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

  await addActionsUser(providerId);
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

export const deleteActions = async (providerId: string): Promise<void> => {
  const { data: { user } } = await supabase.auth.getUser();
  if (!user?.id) throw new Error('User not authenticated');

  // Get all actions for the provider
  const { data: actions, error: actionsError } = await supabase
    .from('provider_actions')
    .select('id')
    .eq('provider_id', providerId);

  if (actionsError) throw actionsError;

  if (actions?.length) {
    const actionIds = actions.map(a => a.id);
    
    const { error: deleteError } = await supabase
      .from('users_provider_actions')
      .delete()
      .eq('user_id', user.id)
      .in('action_id', actionIds);

    if (deleteError) throw deleteError;
  }
};

export const disconnectProvider = async (providerId: string): Promise<void> => {
  const { data: { user } } = await supabase.auth.getUser();

  await deleteActions(providerId);
  
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
    .from('user_provider_custom_auth')
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
    });

  await supabase
    .from('users_oauth_tokens')
    .delete()
    .match({ 
      user_id: user?.id,
      provider_id: providerId 
    });
};

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

  await addActionsUser(providerId);
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

  // TODO: explore if we need to cast scopes from old format here (looks like no)

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

export const addUserMemoryChunk = async (memory: string, tool: string): Promise<any> => {
  const { data: { user } } = await supabase.auth.getUser()
  try {
    const { data, error } = await supabase
      .from('users_memory')
      .insert({
        user_id: user?.id,
        memory: memory,
        tool: tool,
        created_at: new Date().toISOString()
      })
      .select()
      .single();
    
    if (error) throw error;
    return data;
  } catch (error) {
    console.error('Error adding memory chunk:', error);
    throw error;
  }
};

export const updateUserMemoryChunk = async (chunkId: string, memory: string, tool: string): Promise<any> => {
  const { data: { user } } = await supabase.auth.getUser()
  try {
    const { data, error } = await supabase
      .from('users_memory')
      .update({ memory, tool })
      .eq('id', chunkId)
      .eq('user_id', user?.id)
      .select()
      .single();
    
    if (error) throw error;
    return data;
  } catch (error) {
    console.error('Error updating memory chunk:', error);
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

export const enableApiKeyWithBaseProvider = async (providerId: string, apiKey: string, baseUrl: string): Promise<void> => {
  const { data: { user } } = await supabase.auth.getUser();
  
  if (!apiKey || !baseUrl) {
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
  
  const raw_data = JSON.stringify({ base_url: baseUrl });
  
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
      .update({ 
        api_key: encryptedKey,
        raw_data: raw_data
      })
      .eq('id', existingKey.id);
    
    apiKeyError = error;
  } else {
    const { error } = await supabase
      .from('users_provider_api_keys')
      .insert({
        user_id: user?.id,
        provider_id: providerId,
        api_key: encryptedKey,
        raw_data: raw_data
      });
    
    apiKeyError = error;
  }

  if (apiKeyError) throw apiKeyError;

  await addActionsUser(providerId);
}

export const getProviderBaseUrl = async (providerId: string): Promise<string | null> => {
  const { data: { user } } = await supabase.auth.getUser();
  
  const { data, error } = await supabase
    .from('users_provider_api_keys')
    .select('raw_data')
    .eq('user_id', user?.id)
    .eq('provider_id', providerId)
    .single();
  
  if (error || !data || !data.raw_data) return null;
  
  try {
    const rawData = JSON.parse(data.raw_data);
    return rawData.base_url || null;
  } catch (error) {
    console.error('Error parsing raw_data:', error);
    return null;
  }
}

export const getProviderCustomAuth = async (providerId: string): Promise<Record<string, any> | null> => {
  const { data: { user } } = await supabase.auth.getUser();
  
  const { data: provider } = await supabase
    .from('providers')
    .select('provider_tag, auth_schema')
    .eq('id', providerId)
    .single();
    
  if (!provider) return null;
  
  try {
    const { data, error } = await supabase
      .from('user_provider_custom_auth')
      .select('raw_data')
      .eq('user_id', user?.id)
      .eq('provider_id', providerId)
      .single();
    
    if (error) {
      if (error.code === 'PGRST116') {
        return null;
      }
      throw error;
    }
    
    if (!data || !data.raw_data) return null;
    
    // Parse raw_data if it's a string
    const rawData = typeof data.raw_data === 'string' 
      ? JSON.parse(data.raw_data) 
      : data.raw_data;
  
    
    return rawData;
  } catch (error) {
    console.error('Error fetching custom auth data:', error);
    return null;
  }
}

export const updateProviderCustomAuth = async (providerId: string, authData: Record<string, any>): Promise<void> => {
  const { data: { user } } = await supabase.auth.getUser();
  
  if (!user?.id) {
    throw new Error("User not authenticated");
  }
  
  const { data: provider } = await supabase
    .from('providers')
    .select('provider_tag, auth_schema')
    .eq('id', providerId)
    .single();
    
  if (!provider) throw new Error('Provider not found');
  
  try {
    // Ensure user is connected to provider
    const { error: providerError } = await supabase
      .from('users_providers')
      .upsert({
        user_id: user.id,
        provider_id: providerId
      }, {
        onConflict: 'provider_id,user_id'
      });

    if (providerError) {
      console.error("Error upserting users_providers:", providerError);
      throw providerError;
    }
    
    // Fetch existing data first
    const { data: existingRecord, error: fetchError } = await supabase
      .from('user_provider_custom_auth')
      .select('id, raw_data')
      .eq('user_id', user.id)
      .eq('provider_id', providerId)
      .single();
    
    let existingData: Record<string, any> = {};
    let recordId: string | null = null;
    
    if (!fetchError && existingRecord) {
      recordId = existingRecord.id;
      existingData = typeof existingRecord.raw_data === 'string' 
        ? JSON.parse(existingRecord.raw_data) 
        : existingRecord.raw_data || {};
    }
    
    // Merge existing data with new data
    const mergedData = { ...existingData, ...authData };
    
    // Process only the new/changed fields to encrypt sensitive values
    const processedAuthData = { ...mergedData };
    const authSchema = Array.isArray(provider.auth_schema) ? provider.auth_schema : [];
    
    for (const field of authSchema) {
      const key = field.key;
      const isSensitive = field.type === 'password' || field.sensitive;
      const valueChanged = authData[key] !== undefined && authData[key] !== existingData[key];
      
      // Only encrypt if: field is sensitive, has a value, and has changed
      if (isSensitive && processedAuthData[key] && valueChanged) {
        console.log(`Encrypting changed/new sensitive field: ${key}`);
        const response = await fetch('/api/encrypt', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ apiKey: processedAuthData[key] })
        });
        
        if (!response.ok) {
          throw new Error(`Failed to encrypt value for ${key}`);
        }
        
        const { encryptedKey } = await response.json();
        processedAuthData[key] = encryptedKey;
      }

      await addActionsUser(providerId);
    }

    
    if (recordId) {
      // Update existing record
      const { error: updateError } = await supabase
        .from('user_provider_custom_auth')
        .update({ raw_data: processedAuthData })
        .eq('id', recordId)
        .eq('user_id', user.id); // Ensure we only update our own record
        
      if (updateError) {
        console.error("Error updating custom auth:", updateError);
        throw updateError;
      }
    } else {
      // Create new record
      const { error: insertError } = await supabase
        .from('user_provider_custom_auth')
        .insert({
          user_id: user.id,
          provider_id: providerId,
          raw_data: processedAuthData
        });
        
      if (insertError) {
        console.error("Error inserting custom auth:", insertError);
        throw insertError;
      }
    }
  } catch (error) {
    console.error('Error updating custom auth data:', error);
    throw error;
  }
}

export const validateCustomAuth = async (providerId: string, authData: Record<string, any>): Promise<{valid: boolean, message: string}> => {
  try {
    const { data: provider } = await supabase
      .from('providers')
      .select('provider_tag, auth_schema')
      .eq('id', providerId)
      .single();
      
    if (!provider) throw new Error('Provider not found');
    if (!provider.auth_schema) return { valid: true, message: 'No auth schema defined, assuming valid' };
    
    const authSchema = Array.isArray(provider.auth_schema) ? provider.auth_schema : [];
    
    // Check for required fields
    const missingRequiredFields = [];
    
    for (const field of authSchema) {
      if (field.required) {
        const value = authData[field.key];
        if (value === undefined || value === null || value === '') {
          missingRequiredFields.push(field.label || field.key);
        }
      }
    }
    
    if (missingRequiredFields.length > 0) {
      return { 
        valid: false, 
        message: `Missing required fields: ${missingRequiredFields.join(', ')}` 
      };
    }
    
    // Validate field types
    const typeErrors = [];
    
    for (const field of authSchema) {
      const value = authData[field.key];
      if (value !== undefined && value !== null && value !== '') {
        // Basic type validation
        switch (field.type) {
          case 'number':
            if (isNaN(Number(value))) {
              typeErrors.push(`${field.label || field.key} must be a number`);
            }
            break;
          case 'email':
            // Simple email validation
            if (!/\S+@\S+\.\S+/.test(value)) {
              typeErrors.push(`${field.label || field.key} must be a valid email address`);
            }
            break;
          case 'url':
            // Simple URL validation
            try {
              new URL(value);
            } catch (error) {
              typeErrors.push(`${field.label || field.key} must be a valid URL`);
            }
            break;
          case 'json':
            // Validate JSON
            if (typeof value === 'string') {
              try {
                JSON.parse(value);
              } catch (error) {
                typeErrors.push(`${field.label || field.key} must be valid JSON`);
              }
            }
            break;
        }
      }
    }
    
    if (typeErrors.length > 0) {
      return { 
        valid: false, 
        message: typeErrors.join('; ') 
      };
    }
    
    return {
      valid: true,
      message: 'Authentication validation completed'
    };
  } catch (error) {
    console.error('Error validating custom auth:', error);
    return { 
      valid: false, 
      message: error instanceof Error ? error.message : 'Unknown error occurred during validation' 
    };
  }
}

export const validateApiKey = async (providerId: string, apiKey: string, baseUrl?: string): Promise<{valid: boolean, message: string}> => {
  try {
    const baseApiUrl = process.env.NEXT_PUBLIC_API_URL || '';
    
    const requestBody: any = { api_key: apiKey };
    if (baseUrl) {
      requestBody.base_url = baseUrl;
    }

    const response = await fetch(`${baseApiUrl}/${providerId}/validate_key`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody),
    });

    if (!response.ok) {
      console.error('API validation response not OK:', response.status, response.statusText);
      return { 
        valid: false, 
        message: `API validation failed: ${response.status} ${response.statusText}` 
      };
    }

    const data = await response.json();
    
    return {
      valid: data.valid,
      message: data.message || 'API key validation completed'
    };
  } catch (error) {
    console.error('Error validating API key:', error);
    return { 
      valid: false, 
      message: error instanceof Error ? error.message : 'Unknown error occurred during validation' 
    };
  }
};


export const addActionsUser = async (providerId: string): Promise<void> => {
  
  const { data: { user } } = await supabase.auth.getUser();

  const userIdToUse = user?.id;

  if (!userIdToUse) {
    console.error('No user ID found in auth context');
    throw new Error('Unauthorized - User ID not found');
  }
  

  const { data: provider, error: providersError } = await supabase
        .from('providers')
        .select('id, name, auth_method')
        .eq('id', providerId).single();

  if (!provider) {
    console.error('Provider not found:', providerId);
    throw new Error('Provider not found');
  }

  console.log('Provider auth method:', provider.auth_method);
  if (provider.auth_method === 'oauth') {
    console.log('Processing OAuth flow');
    const { data: oauthToken, error: tokenError } = await supabase
      .from('users_oauth_tokens')
      .select('scopes')
      .eq('user_id', userIdToUse)
      .eq('provider_id', providerId)
      .single();

    if (tokenError || !oauthToken?.scopes) {
      console.error('Failed to get OAuth token scopes:', tokenError);
      throw new Error('Failed to get OAuth token scopes');
    }

    console.log('Retrieved OAuth scopes:', oauthToken.scopes);
    const { data: scopedActions, error: scopeError } = await supabase
      .from('provider_action_scopes')
      .select('action_id')
      .in('scope_id', oauthToken.scopes)
      .eq('provider_id', providerId);

    if (scopeError) {
      console.error('Error getting scoped actions:', scopeError);
    }
    if (!scopedActions?.length) {
      console.log('No scoped actions found, returning');
      return;
    }

    const actionIds = scopedActions.map(sa => sa.action_id);
    console.log('Found action IDs:', actionIds);

    const { data: actions, error: actionsError } = await supabase
      .from('provider_actions')
      .select('id')
      .eq('provider_id', providerId)
      .in('id', actionIds);

    if (actionsError) {
      console.error('Error getting actions:', actionsError);
    }
    if (!actions?.length) {
      console.log('No actions found, returning');
      return;
    }

    const insertData = actions.map(action => ({
      user_id: user?.id,
      action_id: action.id
    }));

    console.log('Inserting user provider actions:', insertData);
    const { error: insertError } = await supabase
      .from('users_provider_actions')
      .upsert(insertData, {
        onConflict: 'user_id,action_id',
        ignoreDuplicates: true
      });

    if (insertError) {
      console.error('Error inserting actions:', insertError);
      throw insertError;
    }
  } else {
    const { data: actions, error: actionsError } = await supabase
      .from('provider_actions')
      .select('id')
      .eq('provider_id', providerId);

    if (actionsError) {
      console.error('Error getting actions:', actionsError);
      throw actionsError;
    }
    if (!actions?.length) {
      console.log('No actions found, returning');
      return;
    }

    const insertData = actions.map(action => ({
      user_id: user?.id,
      action_id: action.id
    }));

    console.log('Inserting user provider actions:', insertData);
    const { error: insertError } = await supabase
      .from('users_provider_actions')
      .upsert(insertData, {
        onConflict: 'user_id,action_id',
        ignoreDuplicates: true
      });

    if (insertError) {
      console.error('Error inserting actions:', insertError);
      throw insertError;
    }
  }
  console.log('Successfully completed addActionsUser');
};