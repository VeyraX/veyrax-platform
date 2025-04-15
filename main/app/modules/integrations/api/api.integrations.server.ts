import { createClient } from "@/lib/utils/supabase/server";
import { createClient as createServiceClient } from '@supabase/supabase-js';
import { disconnectProvider } from './api.integrations';

export const addActionsUser = async (providerId: string, userId?: string): Promise<void> => {
    let client;
    let userIdToUse = userId;
    
    if (userId) {
        client = createServiceClient(
          process.env.SUPABASE_URL!,
          process.env.SUPABASE_SERVICE_KEY!
        );
    } else {
        client = createClient();
        const { data: { user } } = await client.auth.getUser();
        userIdToUse = user?.id;
    }

    if (!userIdToUse) {
        throw new Error('Unauthorized - User ID not found');
    }
    
    const { data: provider, error: providersError } = await client
          .from('providers')
          .select('id, name, auth_method')
          .eq('id', providerId).single();

    if (!provider) {
        throw new Error('Provider not found');
    }
  
    if (provider.auth_method === 'oauth') {
        const { data: oauthToken, error: tokenError } = await client
            .from('users_oauth_tokens')
            .select('scopes')
            .eq('user_id', userIdToUse)
            .eq('provider_id', providerId)
            .single();

        if (tokenError || !oauthToken?.scopes) {
            throw new Error('Failed to get OAuth token scopes');
        }
  
        const scopesArray = Array.isArray(oauthToken.scopes) 
            ? oauthToken.scopes 
            : oauthToken.scopes.split(',');
      
        const { data: scopedActions, error: scopeError } = await client
            .from('provider_scopes')
            .select('id, scope_id')
            .in('scope_id', scopesArray)
            .eq('provider_id', providerId);

        if (scopeError) {
            throw scopeError;
        }
        if (!scopedActions?.length) {
            return;
        }

        const scopedActionIds = scopedActions.map(action => action.id);

        const { data: providerActionScopes, error } = await client
            .from('provider_action_scopes')
            .select('action_id, scope_id')
            .in('scope_id', scopedActionIds);

        if (error) {
            throw error;
        }
  
        const actionIds = providerActionScopes.map(sa => sa.action_id);

        const { data: actions, error: actionsError } = await client
            .from('provider_actions')
            .select('id')
            .in('id', actionIds);

        if (actionsError) {
            throw actionsError;
        }
        if (!actions?.length) {
            return;
        }
  
        const insertData = actions.map(action => ({
            action_id: action.id,
            user_id: userIdToUse
        }));

        const { error: insertError } = await client
            .from('users_provider_actions')
            .upsert(insertData, {
                onConflict: 'user_id,action_id',
                ignoreDuplicates: true
            });
  
        if (insertError) {
            throw insertError;
        }
    } else {
        const { data: actions, error: actionsError } = await client
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
            action_id: action.id,
            user_id: userIdToUse
        }));

        const { error: insertError } = await client
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

export const enableApiKeyProvider = async (providerId: string, apiKey: string, user_id?: string): Promise<void> => {
    let userId = user_id;
    let client;
    
    if (userId) {
        client = createServiceClient(
          process.env.SUPABASE_URL!,
          process.env.SUPABASE_SERVICE_KEY!
        );
    } else {
        client = createClient();
        const { data: { user } } = await client.auth.getUser();
        userId = user?.id;
    }
    
    if (!apiKey) {
      await disconnectProvider(providerId);
      return;
    }
    
    const { error: providerError } = await client
      .from('users_providers')
      .upsert({
        user_id: userId,
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
    
    const { data: existingKey } = await client
      .from('users_provider_api_keys')
      .select('id')
      .eq('user_id', userId)
      .eq('provider_id', providerId)
      .single();
    
    let apiKeyError;
    
    if (existingKey) {
      const { error } = await client
        .from('users_provider_api_keys')
        .update({ api_key: encryptedKey })
        .eq('id', existingKey.id);
      
      apiKeyError = error;
    } else {
      const { error } = await client
        .from('users_provider_api_keys')
        .insert({
          user_id: userId,
          provider_id: providerId,
          api_key: encryptedKey
        });
      
      apiKeyError = error;
    }
  
    if (apiKeyError) throw apiKeyError;
  
    await addActionsUser(providerId, userId);
  }

export const validateUserAuthentication = async (options: {
  user_id?: string;
  encrypted_api_key?: string;
  code?: string;
}) => {
  const { user_id, encrypted_api_key, code } = options;
  
  if (user_id) {
    return user_id;
  }
  
  if (encrypted_api_key && code) {
    try {
      const { decrypt, decrypt_with_code } = await import('@/lib/utils/encryption');
      
      const decrypted = decrypt(encrypted_api_key);
      const parts = decrypted.split(':');
      
      if (parts.length >= 3) {
        const encryptedUserId = parts[0];
        const providerId = parts[1];
        const storedCode = parts[2];
        
        if (code !== storedCode) {
          throw new Error('Code verification failed');
        }
        
        const userId = decrypt_with_code(encryptedUserId, code);
        if (!userId) {
          throw new Error('Failed to decrypt user ID');
        }
        
        return userId;
      }
    } catch (error) {
      console.error('Error processing API key:', error);
    }
    
    throw new Error('Invalid API key or user not found');
  }
  
  throw new Error('User identification (user_id or encrypted_api_key with code) is required');
};

export const saveApiKey = async (options: {
  user_id: string;
  provider_id: string;
  api_key: string;
  raw_data?: Record<string, any>;
}) => {
  const { user_id, provider_id, api_key, raw_data } = options;
  
  let client;
  
  if (user_id) {
    client = createServiceClient(
      process.env.SUPABASE_URL!,
      process.env.SUPABASE_SERVICE_KEY!
    );
  } else {
    client = createClient();
    const { data: { user } } = await client.auth.getUser();
    if (!user?.id) {
      throw new Error('Unauthorized - User ID not found');
    }
  }
  
  const { error: providerError } = await client
    .from('users_providers')
    .upsert({
      user_id: user_id,
      provider_id: provider_id
    }, {
      onConflict: 'provider_id,user_id'
    });

  if (providerError) {
    throw new Error('Failed to connect provider: ' + providerError.message);
  }
  
  const { encrypt } = await import('@/lib/utils/encryption');
  const encryptedKey = encrypt(api_key);
  
  const { data: existingKey } = await client
    .from('users_provider_api_keys')
    .select('id')
    .eq('user_id', user_id)
    .eq('provider_id', provider_id)
    .single();
  
  let apiKeyError;
  
  if (existingKey) {
    const updateData: any = { api_key: encryptedKey };
    if (raw_data) {
      updateData.raw_data = JSON.stringify(raw_data);
    }
    
    const { error } = await client
      .from('users_provider_api_keys')
      .update(updateData)
      .eq('id', existingKey.id);
    
    apiKeyError = error;
  } else {
    const insertData: any = {
      user_id: user_id,
      provider_id: provider_id,
      api_key: encryptedKey
    };
    
    if (raw_data) {
      insertData.raw_data = JSON.stringify(raw_data);
    }
    
    const { error } = await client
      .from('users_provider_api_keys')
      .insert(insertData);
    
    apiKeyError = error;
  }
  
  if (apiKeyError) {
    throw new Error('Failed to save API key: ' + apiKeyError.message);
  }
  
  await addActionsUser(provider_id, user_id);
  
  return encryptedKey;
};

export const disconnectProviderForUser = async (options: {
  user_id: string;
  provider_id: string;
}) => {
  const { user_id, provider_id } = options;
  
  let client;
  
  if (user_id) {
    client = createServiceClient(
      process.env.SUPABASE_URL!,
      process.env.SUPABASE_SERVICE_KEY!
    );
  } else {
    client = createClient();
    const { data: { user } } = await client.auth.getUser();
    if (!user?.id) {
      throw new Error('Unauthorized - User ID not found');
    }
  }
  
  const { data: actions } = await client
    .from('provider_actions')
    .select('id')
    .eq('provider_id', provider_id);

  if (actions?.length) {
    const actionIds = actions.map(a => a.id);
    
    await client
      .from('users_provider_actions')
      .delete()
      .eq('user_id', user_id)
      .in('action_id', actionIds);
  }
  
  const { data: rentApiKey } = await client
    .from('rent_api_keys')
    .select('id')
    .eq('provider_id', provider_id)
    .single();

    await client
      .from('users_provider_rent_api_keys')
      .delete()
      .match({ 
        user_id: user_id,
        rent_key_id: rentApiKey?.id
      });


  await client
    .from('users_provider_api_keys')
    .delete()
    .match({ 
      user_id: user_id,
      provider_id: provider_id 
    });
    
  await client
    .from('users_db_access')
    .delete()
    .match({ 
      user_id: user_id,
      provider_id: provider_id 
    });
    
  await client
    .from('user_provider_custom_auth')
    .delete()
    .match({ 
      user_id: user_id,
      provider_id: provider_id 
    });
    
  await client
    .from('users_providers')
    .delete()
    .match({ 
      user_id: user_id,
      provider_id: provider_id 
    });
    
  await client
    .from('users_oauth_tokens')
    .delete()
    .match({ 
      user_id: user_id,
      provider_id: provider_id 
    });
};

export const saveDbCredentials = async (options: {
  user_id: string;
  provider_id: string;
  db_config: any;
}) => {
  const { user_id, provider_id, db_config } = options;
  
  let client;
  
  if (user_id) {
    client = createServiceClient(
      process.env.SUPABASE_URL!,
      process.env.SUPABASE_SERVICE_KEY!
    );
  } else {
    client = createClient();
    const { data: { user } } = await client.auth.getUser();
    if (!user?.id) {
      throw new Error('Unauthorized - User ID not found');
    }
  }
  
  const { error: providerError } = await client
    .from('users_providers')
    .upsert({
      user_id: user_id,
      provider_id: provider_id
    }, {
      onConflict: 'provider_id,user_id'
    });

  if (providerError) {
    throw new Error('Failed to connect provider: ' + providerError.message);
  }
  
  const { encrypt } = await import('@/lib/utils/encryption');
  const encryptedPassword = encrypt(db_config.password);
  
  const credentials = {
    ...db_config,
    password: encryptedPassword
  };
  
  const { data: existingCredentials } = await client
    .from('users_db_access')
    .select('id')
    .eq('user_id', user_id)
    .eq('provider_id', provider_id)
    .single();
  
  let dbAccessError;
  
  if (existingCredentials) {
    const { error } = await client
      .from('users_db_access')
      .update({ credentials: JSON.stringify(credentials) })
      .eq('id', existingCredentials.id);
    
    dbAccessError = error;
  } else {
    const { error } = await client
      .from('users_db_access')
      .insert({
        user_id: user_id,
        provider_id: provider_id,
        credentials: JSON.stringify(credentials)
      });
    
    dbAccessError = error;
  }
  
  if (dbAccessError) {
    throw new Error('Failed to save database credentials: ' + dbAccessError.message);
  }
  
  await addActionsUser(provider_id, user_id);
  
  return credentials;
};


export const saveCustomAuth = async (options: {
  user_id: string;
  provider_id: string;
  auth_data: Record<string, any>;
}) => {
  const { user_id, provider_id, auth_data } = options;
  
  let client;
  
  if (user_id) {
    client = createServiceClient(
      process.env.SUPABASE_URL!,
      process.env.SUPABASE_SERVICE_KEY!
    );
  } else {
    client = createClient();
    const { data: { user } } = await client.auth.getUser();
    if (!user?.id) {
      throw new Error('Unauthorized - User ID not found');
    }
  }
  
  const { error: providerError } = await client
    .from('users_providers')
    .upsert({
      user_id: user_id,
      provider_id: provider_id
    }, {
      onConflict: 'provider_id,user_id'
    });

  if (providerError) {
    throw new Error('Failed to connect provider: ' + providerError.message);
  }
  
  const { data: provider, error: providerInfoError } = await client
    .from('providers')
    .select('provider_tag, auth_schema')
    .eq('id', provider_id)
    .single();
    
  if (providerInfoError || !provider) {
    throw new Error(providerInfoError?.message || 'Provider not found');
  }
  
  const { data: existingRecord, error: fetchError } = await client
    .from('user_provider_custom_auth')
    .select('id, raw_data')
    .eq('user_id', user_id)
    .eq('provider_id', provider_id)
    .single();
    
  let existingData: Record<string, any> = {};
  let recordId: string | null = null;
  
  if (!fetchError && existingRecord) {
    recordId = existingRecord.id;
    existingData = typeof existingRecord.raw_data === 'string' 
      ? JSON.parse(existingRecord.raw_data) 
      : existingRecord.raw_data || {};
  }
  
  const mergedData = { ...existingData, ...auth_data };
  
  const { encrypt } = await import('@/lib/utils/encryption');
  const processedAuthData = { ...mergedData };
  const authSchema = Array.isArray(provider.auth_schema) ? provider.auth_schema : [];
  
  for (const field of authSchema) {
    const key = field.key;
    const isSensitive = field.type === 'password' || field.sensitive;
    const valueChanged = auth_data[key] !== undefined && auth_data[key] !== existingData[key];
    
    if (isSensitive && processedAuthData[key] && valueChanged) {
      processedAuthData[key] = encrypt(processedAuthData[key]);
    }
  }
  
  let upsertError;
  
  if (recordId) {
    const { error } = await client
      .from('user_provider_custom_auth')
      .update({ raw_data: processedAuthData })
      .eq('id', recordId)
      .eq('user_id', user_id);
      
    upsertError = error;
  } else {
    const { error } = await client
      .from('user_provider_custom_auth')
      .insert({
        user_id: user_id,
        provider_id: provider_id,
        raw_data: processedAuthData
      });
      
    upsertError = error;
  }
  
  if (upsertError) {
    throw new Error('Failed to save custom auth data: ' + upsertError.message);
  }
  
  await addActionsUser(provider_id, user_id);
  
  return processedAuthData;
};

export const saveEnableProvider = async (options: {
  user_id: string;
  provider_id: string;
}) => {
  const { user_id, provider_id } = options;
  
  let client;
  
  if (user_id) {
    client = createServiceClient(
      process.env.SUPABASE_URL!,
      process.env.SUPABASE_SERVICE_KEY!
    );
  } else {
    client = createClient();
    const { data: { user } } = await client.auth.getUser();
    if (!user?.id) {
      throw new Error('Unauthorized - User ID not found');
    }
  }
  
  const { error: providerError } = await client
    .from('users_providers')
    .upsert({
      user_id: user_id,
      provider_id: provider_id
    }, {
      onConflict: 'provider_id,user_id'
    });

  if (providerError) {
    throw new Error('Failed to connect provider: ' + providerError.message);
  }
  
  await addActionsUser(provider_id, user_id);
};

export const saveEnableWhatsapp = async (options: {
  user_id: string;
  auth_data: any;
}) => {
  const { user_id, auth_data } = options;
  
  if (!auth_data || !auth_data.isLoggedIn) {
    console.error('[saveEnableWhatsapp] Invalid WhatsApp auth data:', JSON.stringify({
      has_auth_data: !!auth_data,
      is_logged_in: auth_data?.isLoggedIn
    }));
    throw new Error('Invalid WhatsApp authentication data');
  }
  
  let client;
  
  if (user_id) {
    client = createServiceClient(
      process.env.SUPABASE_URL!,
      process.env.SUPABASE_SERVICE_KEY!
    );
  } else {
    client = createClient();
    const { data: { user } } = await client.auth.getUser();
    if (!user?.id) {
      console.error('[saveEnableWhatsapp] User not found');
      throw new Error('Unauthorized - User ID not found');
    }
  }
  
  const { data: provider, error: providerError } = await client
    .from('providers')
    .select('id')
    .eq('provider_tag', 'whatsapp')
    .single();
    
  if (providerError || !provider) {
    console.error('[saveEnableWhatsapp] WhatsApp provider not found:', providerError);
    throw new Error('WhatsApp provider not found: ' + (providerError?.message || ''));
  }
  
  const { error: connectionError } = await client
    .from('users_providers')
    .upsert({
      user_id: user_id,
      provider_id: provider.id
    }, {
      onConflict: 'provider_id,user_id'
    });

  if (connectionError) {
    throw new Error('Failed to connect WhatsApp provider: ' + connectionError.message);
  }
  
  const { data: existingAuth } = await client
    .from('user_provider_custom_auth')
    .select('id')
    .eq('user_id', user_id)
    .eq('provider_id', provider.id)
    .single();
    
  let customAuthError;
  
  if (existingAuth) {
    const { error } = await client
      .from('user_provider_custom_auth')
      .update({
        raw_data: auth_data
      })
      .eq('id', existingAuth.id);
      
    customAuthError = error;
  } else {
    const { error } = await client
      .from('user_provider_custom_auth')
      .insert({
        user_id: user_id,
        provider_id: provider.id,
        raw_data: auth_data
      });
      
    customAuthError = error;
  }
    
  if (customAuthError) {
    console.error('[saveEnableWhatsapp] Failed to save auth data:', customAuthError);
    throw new Error('Failed to save WhatsApp authentication data: ' + customAuthError.message);
  }
  
  await addActionsUser(provider.id, user_id);
  
  return true;
};

export const saveDisconnectWhatsapp = async (options: {
  user_id: string;
  access_token?: string;
}) => {
  const { user_id, access_token } = options;
  
  let client;
  let accessToken;
  let userIdToUse = user_id;
  let apiKey;
  
  if (user_id) {
    client = createServiceClient(
      process.env.SUPABASE_URL!,
      process.env.SUPABASE_SERVICE_KEY!
    );
    
    const { data: userData } = await client
      .from('users_api_keys')
      .select('api_key')
      .eq('user_id', user_id)
      .single();
      
    if (userData?.api_key) {
      apiKey = userData.api_key;
    }
  } else {
    client = createClient();
    const { data: { user } } = await client.auth.getUser();
    const { data: { session } } = await client.auth.getSession();
    
    if (!user?.id) {
      throw new Error('Unauthorized - User ID not found');
    }
    userIdToUse = user.id;
    accessToken = session?.access_token;
  }
  
  const { data: provider, error: providerError } = await client
    .from('providers')
    .select('id')
    .eq('provider_tag', 'whatsapp')
    .single();
    
  if (providerError || !provider) {
    throw new Error('WhatsApp provider not found: ' + (providerError?.message || ''));
  }

  try {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || '';
    const headers: Record<string, string> = {
      'Content-Type': 'application/json'
    };

    if (access_token) {
      headers['Authorization'] = `Bearer ${access_token}`;
    }

    if (accessToken) {
      headers['Authorization'] = `Bearer ${accessToken}`;
    }

    if (apiKey) {
      headers['VEYRAX_API_KEY'] = apiKey;
    }

    const response = await fetch(`${apiUrl}/whatsapp/disconnect`, {
      method: 'POST',
      headers,
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('WhatsApp disconnect error:', errorText);
    }
  } catch (error) {
    console.error('Error calling WhatsApp disconnect API:', error);
  }
  
  await disconnectProviderForUser({
    user_id: userIdToUse,
    provider_id: provider.id
  });
  
  return true;
};

export const saveRentApiKey = async (options: {
  user_id: string;
  provider_id: string;
}): Promise<void> => {
  const { user_id, provider_id } = options;
  
  const client = createServiceClient(
    process.env.SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_KEY!
  );

  const { data: apiKeyData } = await client
    .from('rent_api_keys')
    .select('id')
    .eq('provider_id', provider_id)
    .single();
    
  console.log('apiKeyData', apiKeyData);

  const { error: rentError } = await client
    .from('users_provider_rent_api_keys')
    .upsert({
      user_id,
      rent_key_id: apiKeyData?.id
    }, {
      onConflict: 'user_id,rent_key_id'
    });

    if (rentError) {
      throw new Error('Failed to rent API key: ' + rentError.message);
    }

    const { error: providerError } = await client
    .from('users_providers')
    .upsert({
      user_id,
      provider_id
    }, {
      onConflict: 'provider_id,user_id'
    });

  if (providerError) {
    throw new Error('Failed to connect provider: ' + providerError.message);
  }

  await addActionsUser(provider_id, user_id);
};