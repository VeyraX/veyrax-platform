import { createClient } from "@/lib/utils/supabase/server";


export const addActionsUser = async (providerId: string): Promise<void> => {
    const supabase = await createClient();
  
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
  
    if (provider.auth_method === 'oauth') {
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
  

      const { data: scopedActions2, error: scopeError2 } = await supabase
        .from('provider_scopes')
        .select('id, scope_id')
        .eq('provider_id', providerId);
  
      const scopesArray = Array.isArray(oauthToken.scopes) 
        ? oauthToken.scopes 
        : oauthToken.scopes.split(',');
      
      const { data: scopedActions, error: scopeError } = await supabase
        .from('provider_scopes')
        .select('id, scope_id')
        .in('scope_id', scopesArray)
        .eq('provider_id', providerId);
  
      if (scopeError) {
        console.error('Error getting scoped actions:', scopeError);
      }
      if (!scopedActions?.length) {
        console.log('No scoped actions found, returning; all scopes:', scopedActions2, oauthToken.scopes);
        return;
      }
  
      const insertData = scopedActions.map(sa => ({
        action_id: sa.id,
        user_id: user?.id
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