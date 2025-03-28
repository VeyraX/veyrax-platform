import { createClient } from "@/lib/utils/supabase/server";

export const addActionsUser = async (providerId: string): Promise<void> => {
    const supabase = createClient();
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
  
        const scopesArray = Array.isArray(oauthToken.scopes) 
            ? oauthToken.scopes 
            : oauthToken.scopes.split(',');
      
        const { data: scopedActions, error: scopeError } = await supabase
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

        const { data: providerActionScopes, error } = await supabase
            .from('provider_action_scopes')
            .select('action_id, scope_id')
            .in('scope_id', scopedActionIds);

        if (error) {
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