import { createClient } from '@/lib/utils/supabase/server';

export async function getProviderActionsForFlow(userId?: string) {
  try {
    const supabase = createClient();
    
    let queryUserId = userId;
    
    if (!queryUserId) {
      const { data: { user }, error: userError } = await supabase.auth.getUser();
      
      if (userError || !user) {
        throw new Error('Not authenticated');
      }
      
      queryUserId = user.id;
    }
    
    const { data, error } = await supabase
      .from('user_actions_view')
      .select('provider_id, provider_tag, provider_name, action_slug, input_schema, examples, logo_url')
      .eq('user_id', queryUserId);

    if (error) throw error;
    return { data: data || [], error: null };
  } catch (error) {
    console.error('Error fetching actions for flow:', error);
    return { data: [], error };
  }
}

export async function getFlowForPromptServer(flowId?: string, apiKey?: string) {
  if (!flowId) {
    return { data: null, error: null };
  }
  
  try {
    const supabase = createClient();
    let userId;

    if (apiKey) {
      const { data: apiKeyData, error: apiKeyError } = await supabase
        .from('users_api_keys')
        .select('user_id')
        .eq('api_key', apiKey)
        .single();
      
      if (apiKeyError || !apiKeyData) {
        throw new Error('Invalid API key');
      }
      
      userId = apiKeyData.user_id;
    } else {
      const { data: { user }, error: userError } = await supabase.auth.getUser();
      
      if (userError || !user) {
        throw new Error('Not authenticated');
      }
      
      userId = user.id;
    }
    
    const { data, error } = await supabase
      .from('user_flows')
      .select('id, name, description, plain_description')
      .eq('id', flowId)
      .eq('user_id', userId)
      .maybeSingle();
    
    if (error) throw error;
    
    if (!data) {
      return { data: null, error: null };
    }
    
    return { data, error: null };
  } catch (error) {
    console.error('Error fetching flow for prompt:', error);
    return { data: null, error };
  }
}

// Keep the old function for backward compatibility, but make it use the new one
export async function getFlowForPrompt(flowId?: string) {
  return getFlowForPromptServer(flowId);
}