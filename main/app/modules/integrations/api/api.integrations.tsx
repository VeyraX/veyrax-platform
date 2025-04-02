import { createClient } from '@/lib/utils/supabase/client'
import { IntegrationCardProps, Provider, ProviderDetails, ProviderEndpoint, DbConfig, UserDbAccess, ProviderAction, ProviderScope } from './types.integrations'

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

  const { data: userScopes } = await supabase
    .from('user_provider_scopes_view')
    .select('*')
    .eq('user_id', user?.id);

  const result = providers?.map((provider: Provider & { provider_scopes: Array<{ scope_id: string, scope_name: string }> }) => {
    const isConnected = connectedProviderIds.has(provider.id)
    
    const isReallyConnected = provider.auth_method === 'api_key' 
      ? providersWithApiKeys.has(provider.id) 
      : isConnected
    
    const isPopular = popularProviderIds.has(provider.id)

    const providerUserScopes = userScopes?.find(s => s.provider_id === provider.id);
    
    const transformedUserScopes = providerUserScopes ? 
      providerUserScopes.scope_ids.map((scope_id: string, index: number) => ({
        id: `${provider.id}-${scope_id}`,
        scope_id: scope_id,
        scope_name: providerUserScopes.scope_names[index]
      })) : [];

    provider.scopes = provider.provider_scopes?.map(s => ({
      id: s.scope_id,
      scope_id: s.scope_id,
      scope_name: s.scope_name
    })) || []

    return {
      ...provider,
      connected: isReallyConnected,
      isPopular,
      hasIndex: false,
      indexStatus: null,
      lastSyncDate: null,
      processedEntities: null,
      user_scopes: transformedUserScopes
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

  const { data: actions } = await supabase
    .from('provider_actions')
    .select('id')
    .eq('provider_id', providerId);

  if (actions?.length) {
    const actionIds = actions.map(a => a.id);
    
    await supabase
      .from('users_provider_actions')
      .delete()
      .eq('user_id', user.id)
      .in('action_id', actionIds);
  }
};

export const disconnectWhatsAppProvider = async (providerId: string): Promise<void> => {
  const { data: { user } } = await supabase.auth.getUser();

  await fetch('/api/integrations/whatsapp/disconnect', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ providerId })
  });

  await disconnectProvider(providerId);
}

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

export const initiateOAuthFlow = async (providerTag: string, scopes: string[], return_url?: string): Promise<string> => {

  
  const response = await fetch(`/api/oauth/${providerTag}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ scopes, return_url })
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
  const { data: { user } } = await supabase.auth.getUser();

  const { data: provider, error } = await supabase
    .from('providers')
    .select(`
      *,
      provider_scopes (
        scope_id,
        scope_name
      )
    `)
    .eq('provider_tag', providerTag)
    .single();

  if (error) {
    console.error('Error fetching provider details:', error);
    throw error;
  }

  // Convert provider scopes to ProviderScope format
  const scopes = provider.provider_scopes?.map((s: { scope_id: string, scope_name: string }) => ({
    scope_id: s.scope_id,
    scope_name: s.scope_name
  })) || [];

  // Only fetch and process OAuth tokens if the provider uses OAuth
  let userScopes: ProviderScope[] = [];
  if (provider.auth_method === 'oauth') {
    const { data: oauthToken } = await supabase
      .from('users_oauth_tokens')
      .select('scopes')
      .eq('user_id', user?.id)
      .eq('provider_id', provider.id)
      .single();

    // Filter user scopes based on the oauth token scopes
    userScopes = oauthToken?.scopes
      ? scopes.filter((scope: ProviderScope) => oauthToken.scopes.includes(scope.scope_id))
      : [];
  }

  const { data: actions, error: actionsError } = await supabase
    .from('provider_actions')
    .select('*')
    .eq('provider_id', provider.id);

  if (actionsError) {
    console.error('Error fetching provider actions:', actionsError);
    throw actionsError;
  }

  const endpointsList = actions?.map(action => {
    const inputSchema = typeof action.input_schema === 'string' 
      ? JSON.parse(action.input_schema) 
      : action.input_schema;

    return {
      name: action.action_slug,
      functionId: action.action_name,
      description: inputSchema?.function?.description || '',
      paramCount: countParameters(inputSchema),
      input_schema: inputSchema,
      output_schema: typeof action.output_schema === 'string' 
        ? JSON.parse(action.output_schema) 
        : action.output_schema,
      examples: typeof action.examples === 'string'
        ? JSON.parse(action.examples)
        : action.examples
    };
  }) || [];

  const uiComponents = actions?.map(action => {
    if (!action.ui_component) return null;
    
    const component = typeof action.ui_component === 'string'
      ? JSON.parse(action.ui_component)
      : action.ui_component;

    return {
      ...component,
      action_slug: action.action_slug
    };
  }).filter(Boolean) || [];

  const totalEndpoints = endpointsList.length;
  const totalParameters = endpointsList.reduce((sum, endpoint) => sum + endpoint.paramCount, 0);
  const totalComponents = uiComponents.length;

  const inputSchemas: Record<string, any> = {};
  const outputSchemas: Record<string, any> = {};
  const exampleSchema: Record<string, any> = {};

  endpointsList.forEach(endpoint => {
    inputSchemas[endpoint.name] = endpoint.input_schema;
    outputSchemas[endpoint.name] = endpoint.output_schema;
    exampleSchema[endpoint.name] = endpoint.examples;
  });

  // Remove provider_scopes from provider object and add transformed scopes
  const { provider_scopes: _, ...providerWithoutScopes } = provider;
  const providerWithScopes = {
    ...providerWithoutScopes,
    scopes,
    user_scopes: userScopes
  };

  const result: ProviderDetails = {
    provider: {
      ...providerWithScopes,
      input_schema: inputSchemas,
      output_schema: outputSchemas,
      ui_component: uiComponents
    },
    actions: actions || [],
    totalEndpoints,
    totalParameters,
    totalComponents,
    endpointsList,
    exampleSchema
  };

  return result;
};

const countParameters = (schema: any): number => {
  if (!schema?.function?.parameters?.properties) return 0;
  
  let count = 0;
  const props = schema.function.parameters.properties;
  
  for (const [_, prop] of Object.entries(props) as [string, { $ref?: string }][]) {
    count += 1;
    if (prop.$ref && schema.function.parameters.$defs) {
      const defName = prop.$ref.split('/').pop();
      const definition = schema.function.parameters.$defs[defName as string];
      if (definition?.properties) {
        count += Object.keys(definition.properties).length;
      }
    }
  }
  
  return count;
};

export const findComponentForEndpoint = async (providerTag: string, endpointName: string): Promise<any> => {
  const { data: provider } = await supabase
    .from('providers')
    .select('id')
    .eq('provider_tag', providerTag)
    .single();

  if (!provider) {
    return null;
  }

  const { data: action } = await supabase
    .from('provider_actions')
    .select(`
      id,
      action_name,
      action_slug,
      ui_component
    `)
    .eq('provider_id', provider.id)
    .eq('action_slug', endpointName)
    .single();

  if (!action?.ui_component) {
    return null;
  }

  try {
    const rawComponent = typeof action.ui_component === 'string' 
      ? JSON.parse(action.ui_component) 
      : action.ui_component;

    const componentName = Object.keys(rawComponent)[0];
    if (!componentName) {
      return null;
    }

    const componentData = rawComponent[componentName];

    return {
      name: componentName,
      ...componentData,
      action_slug: action.action_slug,
      jsx: componentData.component?.jsx || componentData.jsx || '',
      component: componentData.component || { jsx: componentData.jsx || '' }
    };
  } catch (e) {
    return null;
  }
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

export const validateCustomAuthSchema = async (providerId: string, authData: Record<string, any>): Promise<{valid: boolean, message: string}> => {
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
    throw new Error('Unauthorized - User ID not found');
  }
  

  const { data: provider, error: providersError } = await supabase
        .from('providers')
        .select('id, name, auth_method')
        .eq('id', providerId).single();

  if (!provider) {
    throw new Error('Provider not found');
  }

  if (provider.auth_method === 'oauth') {
    const { data: oauthToken, error: tokenError } = await supabase
      .from('users_oauth_tokens')
      .select('scopes')
      .eq('user_id', userIdToUse)
      .eq('provider_id', providerId)
      .single();

    if (tokenError || !oauthToken?.scopes) {
      throw new Error('Failed to get OAuth token scopes');
    }

    const { data: scopedActions, error: scopeError } = await supabase
      .from('provider_action_scopes')
      .select('action_id')
      .in('scope_id', oauthToken.scopes)
      .eq('provider_id', providerId);

    if (scopeError) {
      throw scopeError;
    }
    if (!scopedActions?.length) {
      return;
    }

    const actionIds = scopedActions.map(sa => sa.action_id);

    const { data: actions, error: actionsError } = await supabase
      .from('provider_actions')
      .select('id')
      .eq('provider_id', providerId)
      .in('id', actionIds);

    if (actionsError) {
      throw actionsError;
    }
    if (!actions?.length) {
      return;
    }

    const insertData = actions.map(action => ({
      user_id: user?.id,
      action_id: action.id
    }));

    const { error: insertError } = await supabase
      .from('users_provider_actions')
      .upsert(insertData, {
        onConflict: 'user_id,action_id',
        ignoreDuplicates: true
      });

    if (insertError) {
      throw insertError;
    }
  } else {
    const { data: actions, error: actionsError } = await supabase
      .from('provider_actions')
      .select('id')
      .eq('provider_id', providerId);

    if (actionsError) {
      throw actionsError;
    }
    if (!actions?.length) {
      return;
    }

    const insertData = actions.map(action => ({
      user_id: user?.id,
      action_id: action.id
    }));

    const { error: insertError } = await supabase
      .from('users_provider_actions')
      .upsert(insertData, {
        onConflict: 'user_id,action_id',
        ignoreDuplicates: true
      });

    if (insertError) {
      throw insertError;
    }
  }
};

export const enableWhatsapp = async (authData: any): Promise<boolean> => {
  if (!authData || !authData.isLoggedIn) {
    return false;
  }

  try {
    const { data: { user } } = await supabase.auth.getUser();
    if (!user?.id) {
      console.error("User not authenticated");
      return false;
    }

    // Get the provider ID for WhatsApp
    const { data: provider } = await supabase
      .from('providers')
      .select('id')
      .eq('provider_tag', 'whatsapp')
      .single();
      
    if (!provider) {
      console.error("WhatsApp provider not found");
      return false;
    }
    
    // Ensure user is connected to WhatsApp provider
    await supabase
      .from('users_providers')
      .upsert({
        user_id: user.id,
        provider_id: provider.id
      }, {
        onConflict: 'provider_id,user_id'
      });
      
    // Save all returned data as raw_data
    await supabase
      .from('user_provider_custom_auth')
      .upsert({
        user_id: user.id,
        provider_id: provider.id,
        raw_data: authData
      }, {
        onConflict: 'user_id,provider_id'
      });
      
    // Enable provider actions
    await addActionsUser(provider.id);
    
    return true;
  } catch (error) {
    console.error("Error enabling WhatsApp:", error);
    return false;
  }
};

export const authenticateWhatsApp = async (): Promise<{success: boolean, qrImageBase64?: string, qrData?: string, isLoggedIn?: boolean, message?: string}> => {
  try {
    const response = await fetch(`/api/integrations/whatsapp/authenticate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      }
    });

    if (!response.ok) {
      throw new Error(`HTTP error ${response.status}: ${await response.text()}`);
    }

    const result = await response.json();
    
    return {
      success: true,
      qrImageBase64: result.data?.qr_image_base64,
      qrData: result.data?.qr_data,
      isLoggedIn: result.data?.is_logged_in,
      message: result.message || 'Authentication started'
    };
  } catch (error) {
    console.error('Error authenticating WhatsApp:', error);
    return {
      success: false,
      message: error instanceof Error ? error.message : 'Failed to authenticate WhatsApp'
    };
  }
};

export const checkWhatsAppStatus = async (): Promise<{success: boolean, isLoggedIn: boolean, phone?: string, message?: string}> => {
  try {
    const response = await fetch(`/api/integrations/whatsapp/check_status`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      }
    });

    if (!response.ok) {
      throw new Error(`HTTP error ${response.status}: ${await response.text()}`);
    }

    const result = await response.json();
    
    return {
      success: true,
      isLoggedIn: result.data?.is_logged_in || false,
      phone: result.data?.phone,
      message: result.message || 'Status check completed'
    };
  } catch (error) {
    console.error('Error checking WhatsApp status:', error);
    return {
      success: false,
      isLoggedIn: false,
      message: error instanceof Error ? error.message : 'Failed to check WhatsApp status'
    };
  }
};