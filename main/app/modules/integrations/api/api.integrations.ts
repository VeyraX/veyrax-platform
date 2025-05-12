import { getCacheItem, setCacheItem, deleteCacheItem, CacheStore } from '@/lib/utils/index-db'
import { createClient } from '@/lib/utils/supabase/client'
import { IntegrationCardProps, Provider, ProviderDetails, ProviderEndpoint, DbConfig, UserDbAccess, ProviderAction, ProviderScope } from './types.integrations'

const supabase = createClient()

const CACHE_KEYS = {
  INTEGRATIONS_DATA: 'integrations_data',
  USER_CONNECTED_TOOLS: 'user_connected_tools',
  TOP_CONNECTED_PROVIDERS: 'top_connected_providers'
};

export const getTopConnectedProviders = async (): Promise<{ provider_id: string, name: string, provider_tag: string, count_of_users: number }[]> => {
  try {
    const cachedData = await getCacheItem<{ provider_id: string, name: string, provider_tag: string, count_of_users: number }[]>(
      CacheStore.INTEGRATIONS,
      CACHE_KEYS.TOP_CONNECTED_PROVIDERS,
      'global'
    );
    
    if (cachedData) {
      return cachedData;
    }
    
    const response = await fetch('/api/integrations/top-providers');
    
    if (!response.ok) {
      throw new Error(`Failed to fetch top providers: ${response.status} ${response.statusText}`);
    }
    
    const result = await response.json();
    
    if (!result) {
      return [];
    }
    
    await setCacheItem(
      CacheStore.INTEGRATIONS,
      CACHE_KEYS.TOP_CONNECTED_PROVIDERS,
      'global',
      result
    );
    
    return result;
  } catch (error) {
    return [];
  }
};

export const getIntegrationsData = async (): Promise<IntegrationCardProps[]> => {
  try {
    const { data: { user } } = await supabase.auth.getUser();
    const userId = user?.id;
    
    if (userId) {
      const cachedData = await getCacheItem<IntegrationCardProps[]>(
        CacheStore.INTEGRATIONS,
        CACHE_KEYS.INTEGRATIONS_DATA, 
        userId
      );
      if (cachedData) {
        return cachedData;
      }
    }
    
    const response = await fetch('/api/integrations/providers');
    
    if (!response.ok) {
      throw new Error(`Failed to fetch providers: ${response.status} ${response.statusText}`);
    }
    
    const integrations = await response.json();
    
    if (!integrations) {
      throw new Error('No integrations data returned from API');
    }
    
    let userConnections: { provider_id: string }[] = [];
    if (userId) {
      const { data: connections, error: connectionsError } = await supabase
        .from('users_providers')
        .select('provider_id')
        .eq('user_id', userId);
      
      if (!connectionsError) {
        userConnections = connections || [];
      }
    }
    
    const topConnectedProviders = await getTopConnectedProviders();
    
    let result: IntegrationCardProps[] = integrations.map((integration: any) => {
      const connectedData = topConnectedProviders.find(
        provider => provider.provider_id === integration.id
      );
      
      const userCount = connectedData?.count_of_users || 0;
      
      const scopes = integration.provider_scopes ? 
        integration.provider_scopes.map((scope: { id: string, scope_id: string, scope_name: string }) => ({
          id: scope.id,
          scope_id: scope.scope_id,
          scope_name: scope.scope_name
        })) : [];
      
      return {
        id: integration.id,
        name: integration.name,
        description: integration.description,
        logo_url: integration.logo_url,
        categories: integration.categories,
        provider_tag: integration.provider_tag,
        auth_method: integration.auth_method,
        auth_schema: integration.auth_schema,
        scopes: scopes,
        is_enabled: integration.is_enabled,
        connected: userConnections.some(conn => conn.provider_id === integration.id),
        hasIndex: false,
        indexStatus: null,
        count_of_users: userCount
      };
    });
    
    result = result.sort((a, b) => (b.count_of_users || 0) - (a.count_of_users || 0));
    
    const hasRequestCard = result.some(item => item.provider_tag === 'integration-request');
    
    if (!hasRequestCard) {
      result.push({
        id: 'integration-request',
        name: 'Request Integration',
        description: 'Request any integration we missed, and we\'ll work on adding!',
        logo_url: '/integration-request.svg',
        provider_tag: 'integration-request',
        auth_method: 'none',
        connected: false,
        hasIndex: false,
        indexStatus: null,
        count_of_users: 0
      } as IntegrationCardProps);
    }
    
    // Cache the result if user is logged in
    if (userId) {
      await setCacheItem(
        CacheStore.INTEGRATIONS,
        CACHE_KEYS.INTEGRATIONS_DATA, 
        userId, 
        result
      );
    }
    
    return result;
  } catch (error) {
    throw error;
  }
};

export const enableProvider = async (providerId: string, encrypted_api_key?: string, code?: string): Promise<void> => {
  const { data: { user } } = await supabase.auth.getUser();
  
  try {
    const response = await fetch('/api/integrations/enable', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        provider_id: providerId,
        user_id: user?.id,
        encrypted_api_key: encrypted_api_key,
        code: code
      })
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to enable provider');
    }
    
    if (user?.id) {
      await clearUserIntegrationCache(user.id);
    }
  } catch (error) {
    throw error;
  }
}

export const enableDbAccessProvider = async (providerId: string, dbConfig: DbConfig, encrypted_api_key?: string, code?: string): Promise<void> => {
  const { data: { user } } = await supabase.auth.getUser();
  
  try {    
    const response = await fetch('/api/integrations/enable-db-access', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        provider_id: providerId,
        db_config: dbConfig,
        user_id: user?.id,
        encrypted_api_key: encrypted_api_key,
        code: code
      })
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to enable database access');
    }
    
    if (user?.id) {
      await clearUserIntegrationCache(user.id);
    }
  } catch (error) {
    throw error;
  }
}

export const getUserDbCredentials = async (providerId: string, user_id?: string): Promise<DbConfig | null> => {
  let userId = user_id;

  if (!userId) {
    const { data: { user } } = await supabase.auth.getUser();
    userId = user?.id;
  }

  if (!userId) {
    throw new Error('Unauthorized - User ID not found');
  }
  
  const { data, error } = await supabase
    .from('users_db_access')
    .select('credentials')
    .eq('user_id', userId)
    .eq('provider_id', providerId)
    .single();
  
  if (error || !data) return null;
  
  try {
    const credentials = JSON.parse(data.credentials) as DbConfig;
    
    return credentials;
  } catch (error) {
    return null;
  }
}

export const deleteActions = async (providerId: string, encrypted_api_key?: string): Promise<void> => {
  let userId;

  if (!encrypted_api_key) {
    const { data: { user } } = await supabase.auth.getUser();
    userId = user?.id;
    
    if (!userId) {
      throw new Error('Unauthorized - User ID not found');
    }
  }

  const { data: actions } = await supabase
    .from('provider_actions')
    .select('id')
    .eq('provider_id', providerId);

  if (actions?.length) {
    const actionIds = actions.map(a => a.id);
    
    await supabase
      .from('users_provider_actions')
      .delete()
      .eq('user_id', userId)
      .in('action_id', actionIds);
  }
};

export const disconnectWhatsAppProvider = async (providerId: string, encrypted_api_key?: string, code?: string): Promise<void> => {
  let userId;
  
  if (!encrypted_api_key) {
    const { data: { user } } = await supabase.auth.getUser();
    userId = user?.id;
    
    if (!userId) {
      throw new Error('Unauthorized - User ID not found');
    }
  }

  try {
    const response = await fetch('/api/integrations/whatsapp/disconnect', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        provider_id: providerId, 
        user_id: userId,
        encrypted_api_key: encrypted_api_key,
        code: code
      })
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to disconnect WhatsApp provider');
    }
  } catch (error) {
    throw error;
  }
}

export const disconnectProvider = async (providerId: string, encrypted_api_key?: string, code?: string): Promise<void> => {
  const { data: { user } } = await supabase.auth.getUser();

  try {
    const response = await fetch('/api/integrations/disconnect', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        provider_id: providerId,
        user_id: user?.id,
        encrypted_api_key: encrypted_api_key,
        code: code
      })
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to disconnect provider');
    }
    
    if (user?.id) {
      await deleteCacheItem(CacheStore.INTEGRATIONS, CACHE_KEYS.INTEGRATIONS_DATA, user.id);
      await deleteCacheItem(CacheStore.INTEGRATIONS, CACHE_KEYS.USER_CONNECTED_TOOLS, user.id);
    }
  } catch (error) {
    throw error;
  }
};

export const initiateOAuthFlow = async (
  providerTag: string, 
  scopes: string[], 
  return_url?: string,
  encrypted_api_key?: string,
  code?: string
): Promise<string> => {

  const response = await fetch(`/api/oauth/${providerTag}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ scopes, return_url, encrypted_api_key, code })
  });
  
  const { url } = await response.json();
  
  const { data: { user } } = await supabase.auth.getUser();
  if (user?.id) {
    await clearUserIntegrationCache(user.id);
  }
  
  return url;
}

export const enableApiKeyProvider = async (providerId: string, apiKey: string, encrypted_api_key?: string, code?: string): Promise<void> => {
  const { data: { user } } = await supabase.auth.getUser();
  
  try {
    const response = await fetch('/api/integrations/enable-api-key', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        provider_id: providerId,
        api_key: apiKey,
        user_id: user?.id,
        encrypted_api_key: encrypted_api_key,
        code: code
      })
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to enable API key provider');
    }
    
    if (user?.id) {
      await clearUserIntegrationCache(user.id);
    }
  } catch (error) {
    throw error;
  }
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
  
  if (!user?.id) {
    return [];
  }
  
  const cachedData = await getCacheItem<{ providerTag: string, logoUrl: string, isConnected: boolean }[]>(
    CacheStore.INTEGRATIONS,
    CACHE_KEYS.USER_CONNECTED_TOOLS, 
    user.id
  );
  
  if (cachedData) {
    return cachedData;
  }
  
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
  
  const result = userProviders.map(up => {
    return {
      providerTag: up.providers.provider_tag,
      logoUrl: up.providers.logo_url,
      isConnected: true
    };
  }) || [];
  
  await setCacheItem(
    CacheStore.INTEGRATIONS,
    CACHE_KEYS.USER_CONNECTED_TOOLS, 
    user.id, 
    result
  );
  
  return result;
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
    throw error;
  }

  const scopes = provider.provider_scopes?.map((s: { scope_id: string, scope_name: string }) => ({
    scope_id: s.scope_id,
    scope_name: s.scope_name
  })) || [];

  let userScopes: ProviderScope[] = [];
  if (provider.auth_method === 'oauth' && user?.id) {
    try {
      const { data: oauthToken } = await supabase
        .from('users_oauth_tokens')
        .select('scopes')
        .eq('user_id', user.id)
        .eq('provider_id', provider.id)
        .single();

      userScopes = oauthToken?.scopes
        ? scopes.filter((scope: ProviderScope) => oauthToken.scopes.includes(scope.scope_id))
        : [];
    } catch (error) {
    }
  }

  const { data: actions, error: actionsError } = await supabase
    .from('provider_actions')
    .select('*')
    .eq('provider_id', provider.id);

  if (actionsError) {
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

export const testDbConnection = async (providerId: string, dbConfig: DbConfig, encrypted_api_key?: string, code?: string ): Promise<{success: boolean, message: string}> => {
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
        dbConfig,
        encrypted_api_key,
        code
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
    throw error;
  }
};

export const enableApiKeyWithBaseProvider = async (providerId: string, apiKey: string, baseUrl: string, encrypted_api_key?: string, code?: string): Promise<void> => {
  const { data: { user } } = await supabase.auth.getUser();
  
  try {
    const response = await fetch('/api/integrations/enable-api-key-with-base', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        provider_id: providerId,
        api_key: apiKey,
        base_url: baseUrl,
        user_id: user?.id,
        encrypted_api_key: encrypted_api_key,
        code: code
      })
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to enable API key with base URL');
    }
    
    if (user?.id) {
      await clearUserIntegrationCache(user.id);
    }
  } catch (error) {
    throw error;
  }
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
    return null;
  }
}

export const updateProviderCustomAuth = async (providerId: string, authData: Record<string, any>, encrypted_api_key?: string, code?: string): Promise<void> => {
  let userId;
  
  if (!encrypted_api_key) {
    const { data: { user } } = await supabase.auth.getUser();
    userId = user?.id;
    
    if (!userId) {
      throw new Error('Unauthorized - User ID not found');
    }
  }
  
  try {
    const response = await fetch('/api/integrations/update-custom-auth', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        provider_id: providerId,
        auth_data: authData,
        user_id: userId,
        encrypted_api_key: encrypted_api_key,
        code: code
      })
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to update custom authentication');
    }
    
    if (userId) {
      await clearUserIntegrationCache(userId);
    }
  } catch (error) {
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

    const baseApiUrl = process.env.NEXT_PUBLIC_API_URL || '';
    const response = await fetch(`${baseApiUrl}/${provider.provider_tag}/validate_key`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(authData),
    });

    if (!response.ok) {
      return { 
        valid: false, 
        message: `API validation failed: ${response.status} ${response.statusText}` 
      };
    }

    const data = await response.json();
    return {
      valid: data.valid,
      message: data.message || 'Authentication validation completed'
    };

  } catch (error) {
    return { 
      valid: false, 
      message: error instanceof Error ? error.message : 'Unknown error occurred during validation' 
    };
  }
};

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
    return { 
      valid: false, 
      message: error instanceof Error ? error.message : 'Unknown error occurred during validation' 
    };
  }
};


export const addActionsUser = async (providerId: string, user_id?: string): Promise<void> => {
  let userId = user_id;

  if (!userId) {
    const { data: { user } } = await supabase.auth.getUser();
    userId = user?.id;
  }

  if (!userId) {
    throw new Error('Unauthorized - User ID not found');
  }

  const { data: provider, error: providersError } = await supabase
        .from('providers')
        .select('id, name, auth_method, provider_tag')
        .eq('id', providerId).single();

  if (!provider) {
    throw new Error('Provider not found');
  }

  if (provider.auth_method === 'oauth') {
    const { data: oauthToken, error: tokenError } = await supabase
      .from('users_oauth_tokens')
      .select('scopes')
      .eq('user_id', userId)
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
      user_id: userId,
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
      .select('id, action_slug')
      .eq('provider_id', providerId);

    if (actionsError) {
      throw actionsError;
    }
    if (!actions?.length) {
      return;
    }

    let actionsToInsert = actions;

    if (provider.provider_tag === 'linkedin' || provider.provider_tag === 'x') {
      const { data: customAuth, error: customAuthError } = await supabase
        .from('user_provider_custom_auth')
        .select('raw_data')
        .eq('user_id', userId)
        .eq('provider_id', providerId)
        .single();
      
      const actionIdsToRemove = actions.filter(action => action.action_slug == 'get_me').map(action => action.id);
      
      if (customAuth && customAuth.raw_data) {
        const rawData = typeof customAuth.raw_data === 'string' 
          ? JSON.parse(customAuth.raw_data) 
          : customAuth.raw_data || {};
          
        if (!rawData.username) {
          actionsToInsert = actions.filter(action => !actionIdsToRemove.includes(action.id));

          const { error: deleteError } = await supabase
            .from('users_provider_actions')
            .delete()
            .match({ user_id: userId })
            .in('action_id', actionIdsToRemove);

          if (deleteError) {
            throw deleteError;
          }
        }
      }
    }

    const insertData = actionsToInsert.map(action => ({
      user_id: userId,
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

export const enableWhatsapp = async (authData: any, encrypted_api_key?: string, code?: string): Promise<boolean> => {
  if (!authData || !authData.isLoggedIn) {
    return false;
  }

  try {
    let userId;

    if (!encrypted_api_key) {
      const { data: { user } } = await supabase.auth.getUser();
      userId = user?.id;
      
      if (!userId) {
        throw new Error('Unauthorized - User ID not found');
      }
    }

    const response = await fetch('/api/integrations/whatsapp/enable', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        auth_data: authData,
        user_id: userId,
        encrypted_api_key: encrypted_api_key,
        code: code
      })
    });
    
    if (!response.ok) {
      return false;
    }
    
    return true;
  } catch (error) {
    return false;
  }
};

export const authenticateWhatsApp = async (encrypted_api_key?: string, code?: string): Promise<{success: boolean, qrImageBase64?: string, qrData?: string, isLoggedIn?: boolean, message?: string, code?: string, encrypted_api_key?: string}> => {
  try {
    const requestBody: any = {};
    
    if (encrypted_api_key) {
      requestBody.encrypted_api_key = encrypted_api_key;
    }
    
    if (code) {
      requestBody.code = code;
    }
    
    const response = await fetch(`/api/integrations/whatsapp/authenticate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody)
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
      message: result.message || 'Authentication started',
      code: result.data?.code,
      encrypted_api_key: result.data?.encrypted_api_key
    };
  } catch (error) {
    return {
      success: false,
      message: error instanceof Error ? error.message : 'Failed to authenticate WhatsApp'
    };
  }
};

export const checkWhatsAppStatus = async (encrypted_api_key?: string, code?: string): Promise<{success: boolean, isLoggedIn: boolean, phone?: string, message?: string, encrypted_api_key?: string, code?: string}> => {
  try {
    const requestBody: any = {};
    
    if (encrypted_api_key) {
      requestBody.encrypted_api_key = encrypted_api_key;
    }
    
    if (code) {
      requestBody.code = code;
    }
    
    const response = await fetch(`/api/integrations/whatsapp/check_status`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody)
    });

    if (!response.ok) {
      throw new Error(`HTTP error ${response.status}: ${await response.text()}`);
    }

    const result = await response.json();
    
    return {
      success: true,
      isLoggedIn: result.data?.is_logged_in || false,
      phone: result.data?.phone,
      message: result.message || 'Status check completed',
      encrypted_api_key: result.data?.encrypted_api_key,
      code: result.data?.code
    };
  } catch (error) {
    return {
      success: false,
      isLoggedIn: false,
      message: error instanceof Error ? error.message : 'Failed to check WhatsApp status'
    };
  }
};

export const rentApiKey = async (providerId: string, encrypted_api_key?: string, code?: string): Promise<void> => {
  const { data: { user } } = await supabase.auth.getUser();
  
  try {
    const response = await fetch('/api/integrations/rent-api-key', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        provider_id: providerId,
        user_id: user?.id,
        encrypted_api_key,
        code
      })
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to rent API key');
    }
  } catch (error) {
    throw error;
  }
};

export const checkUserHasRentedKey = async (providerId: string): Promise<boolean> => {
  const { data: { user } } = await supabase.auth.getUser();
  
  try {
    const { data: rentApiKey, error: rentApiKeyError } = await supabase
      .from('rent_api_keys')
      .select('id')
      .eq('provider_id', providerId)
      .single();
    
    if (rentApiKeyError || !rentApiKey?.id) return false;
    
    const { data, error } = await supabase
      .from('users_provider_rent_api_keys')
      .select('*')
      .match({ 
        user_id: user?.id,
        rent_key_id: rentApiKey.id
      })
      .single();
    
    if (error || !data) return false;
    
    return true;
  } catch (error) {
    return false;
  }
};

export const getProviderAuthInfo = async (providerTag: string): Promise<{
  id: string;
  name: string;
  auth_method: string;
  logo_url: string;
  provider_tag: string;
  scopes: ProviderScope[];
  auth_schema?: any[];
} | null> => {
  try {
    const { data: provider, error } = await supabase
      .from('providers')
      .select(`
        id,
        name,
        auth_method,
        logo_url,
        provider_tag,
        auth_schema,
        provider_scopes (
          id,
          scope_id,
          scope_name
        )
      `)
      .eq('provider_tag', providerTag)
      .single();
    
    if (error) {
      return null;
    }
    
    const scopes = provider.provider_scopes?.map((s: { id: string, scope_id: string, scope_name: string }) => ({
      id: s.id,
      scope_id: s.scope_id,
      scope_name: s.scope_name
    })) || [];
    
    const { provider_scopes: _, ...providerData } = provider;
    
    return {
      ...providerData,
      scopes
    };
  } catch (error) {
    return null;
  }
};

export const clearUserIntegrationCache = async (userId: string): Promise<void> => {
  try {
    const { clearUserStoreCache } = await import('@/lib/utils/index-db');
    await clearUserStoreCache(CacheStore.INTEGRATIONS, userId);
  } catch (error) {
  }
};