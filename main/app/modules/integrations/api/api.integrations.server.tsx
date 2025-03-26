import { createClient } from "@/lib/utils/supabase/server";


export const addActionsUser = async (providerId: string): Promise<void> => {
    const supabase = createClient();
    const { data: { user } } = await supabase.auth.getUser();
    const userIdToUse = user?.id;

    if (!userIdToUse) {
      console.error('No user ID found in auth context');
      throw new Error('Unauthorized - User ID not found');
    }
    
    // Get provider details
    const { data: provider, error: providersError } = await supabase
          .from('providers')
          .select('id, name, auth_method')
          .eq('id', providerId).single();
  
    if (!provider) {
      console.error('Provider not found:', providerId);
      throw new Error('Provider not found');
    }
  
    if (provider.auth_method === 'oauth') {
      // OAuth flow - get scopes from token and find associated actions
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
  
      // Parse the scopes string into an array
      const scopesArray = Array.isArray(oauthToken.scopes) 
        ? oauthToken.scopes 
        : oauthToken.scopes.split(',');
      
      // Get actions linked to the granted scopes
      const { data: scopedActions, error: scopeError } = await supabase
        .from('provider_scopes')
        .select('id, scope_id')
        .in('scope_id', scopesArray)
        .eq('provider_id', providerId);
  
      if (scopeError) {
        console.error('Error getting scoped actions:', scopeError);
      }
      if (!scopedActions?.length) {
        return;
      }

      const scopedActionIds = scopedActions.map(action => action.id);

      const { data: providerActionScopes, error } = await supabase
        .from('provider_action_scopes')
        .select('action_id, scope_id')
        .in('scope_id', scopedActionIds);
      
      if (error) {
        console.error('Error getting provider action scopes:', error);
        throw error;
      }
  
      const insertData = providerActionScopes.map(sa => ({
        action_id: sa.action_id,
        user_id: user?.id
      }));
  
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
      // Non-OAuth flow (existing implementation)
      const { data: actions, error: actionsError } = await supabase
        .from('provider_actions')
        .select('id')
        .eq('provider_id', providerId);
  
      if (actionsError) {
        console.error('Error getting actions:', actionsError);
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
        console.error('Error inserting actions:', insertError);
        throw insertError;
      }
    }
  };