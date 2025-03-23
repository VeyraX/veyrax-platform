import { createClient } from '@/lib/utils/supabase/client'
import { ProviderAction } from './types.flows'



  const supabase = createClient();
  
  export const getProviderActions = async (providerId: string): Promise<ProviderAction[]> => {
    try {
      const { data, error } = await supabase
        .from('provider_actions')
        .select('*')
        .eq('provider_id', providerId);
      
      if (error) throw error;
      return data || [];
    } catch (error) {
      console.error('Error fetching provider actions:', error);
      throw error;
    }
  };
  
  export const addProviderAction = async (providerId: string, actionName: string): Promise<ProviderAction> => {
    try {
      const { data, error } = await supabase
        .from('provider_actions')
        .insert({
          provider_id: providerId,
          action_name: actionName
        })
        .select()
        .single();
      
      if (error) throw error;
      return data;
    } catch (error) {
      console.error('Error adding provider action:', error);
      throw error;
    }
  };
  
  export const deleteProviderAction = async (actionId: string): Promise<void> => {
    try {
      const { error } = await supabase
        .from('provider_actions')
        .delete()
        .eq('id', actionId);
      
      if (error) throw error;
    } catch (error) {
      console.error('Error deleting provider action:', error);
      throw error;
    }
  };

  export const getAllProviderActions = async () => {
    try {
      const { data, error } = await supabase
        .from('provider_actions')
        .select('provider_id, provider_name, action_name, logo_url');
      
      if (error) throw error;
      return data || [];
    } catch (error) {
      console.error('Error fetching actions:', error);
      throw error;
    }
  };

  export const improveFlowDescription = async (description: string): Promise<string> => {
    try {
      const response = await fetch('/api/flow/improve-description', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ description }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to improve description');
      }
      
      const data = await response.json();
      return data.completion || '';
    } catch (error) {
      console.error('Error improving description:', error);
      throw error;
    }
  };