import { createClient } from '@/lib/utils/supabase/client'
import { ProviderAction, UserFlow, FlowStatus, CreateFlowRequest, UpdateFlowRequest } from './types.flows'
import { extractTextFromHTML as originalExtractTextFromHTML } from '../components/flow-description-html'
import { canUserCreateFlow } from '@/app/modules/settings/api/api.settings'
import { toast } from 'sonner';

const supabase = createClient();

export const getUserActions = async (): Promise<ProviderAction[]> => {
  try {
    const { data: { user } } = await supabase.auth.getUser();
    
    if (!user) {
      throw new Error('Not authenticated');
    }
    
    const { data, error } = await supabase
      .from('user_actions_view')
      .select('*')
      .eq('user_id', user.id);
    
    if (error) throw error;
    return data || [];
  } catch (error) {
    console.error('Error fetching user actions:', error);
    throw error;
  }
};

export const getActionsByProvider = async (providerId: string): Promise<ProviderAction[]> => {
  try {
    const { data: { user } } = await supabase.auth.getUser();
    
    if (!user) {
      throw new Error('Not authenticated');
    }
    
    const { data, error } = await supabase
      .from('user_actions_view')
      .select('*')
      .eq('user_id', user.id)
      .eq('provider_id', providerId);
    
    if (error) throw error;
    return data || [];
  } catch (error) {
    console.error('Error fetching actions by provider:', error);
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

export const getUserFlows = async (): Promise<UserFlow[]> => {
  try {
    const { data: { user } } = await supabase.auth.getUser();
    
    if (!user) {
      throw new Error('Not authenticated');
    }
    
    const { data, error } = await supabase
      .from('user_flows')
      .select('*')
      .eq('user_id', user.id);
    
    if (error) throw error;
    return data || [];
  } catch (error) {
    console.error('Error fetching user flows:', error);
    throw error;
  }
};

export const getFlowById = async (flowId: string): Promise<UserFlow> => {
  try {
    const { data: { user } } = await supabase.auth.getUser();
    
    if (!user) {
      throw new Error('Not authenticated');
    }
    
    const { data, error } = await supabase
      .from('user_flows')
      .select('*')
      .eq('id', flowId)
      .eq('user_id', user.id)
      .single();
    
    if (error) throw error;
    return data;
  } catch (error) {
    console.error('Error fetching flow by ID:', error);
    throw error;
  }
};

export const getPublicFlowById = async (flowId: string): Promise<UserFlow | null> => {
  try {
    const { data, error } = await supabase
      .from('user_flows')
      .select('*')
      .eq('id', flowId)
      .eq('is_shared', true)
      .single();
    
    if (error) {
      console.error('Error fetching public flow:', error);
      return null;
    }
    
    return data;
  } catch (error) {
    console.error('Error fetching public flow:', error);
    return null;
  }
};

export const getFlowActions = async (flowId: string): Promise<string[]> => {
  try {
    const { data, error } = await supabase
      .from('flow_actions')
      .select('action_id')
      .eq('flow_id', flowId);
    
    if (error) throw error;
    return data?.map(item => item.action_id) || [];
  } catch (error) {
    console.error('Error fetching flow actions:', error);
    throw error;
  }
};

export const getPublicFlowActions = async (flowId: string): Promise<string[]> => {
  try {
    const { data: flowData, error: flowError } = await supabase
      .from('user_flows')
      .select('is_shared')
      .eq('id', flowId)
      .single();
    
    if (flowError) throw flowError;
    
    if (!flowData || !flowData.is_shared) {
      return [];
    }
    
    const { data, error } = await supabase
      .from('flow_actions')
      .select('action_id')
      .eq('flow_id', flowId);
      
    if (error) throw error;
    return data?.map(item => item.action_id) || [];
  } catch (error) {
    console.error('Error fetching public flow actions:', error);
    return [];
  }
};

export const getActionsByIds = async (actionIds: string[]): Promise<any[]> => {
  try {
    if (!actionIds.length) return [];
    
    const { data, error } = await supabase
      .from('provider_actions')
      .select('id, action_name, action_slug, provider_id')
      .in('id', actionIds);

    
    if (error) throw error;
    
    const providerIds = Array.from(new Set(data?.map(item => item.provider_id) || []));
    
    if (!providerIds.length) return [];
    
    const { data: providersData, error: providersError } = await supabase
      .from('providers')
      .select('id, name, logo_url')
      .in('id', providerIds);
    
    if (providersError) throw providersError;
    
    return (data || []).map(action => {
      const provider = providersData?.find(p => p.id === action.provider_id) || { name: '', logo_url: '' };
      return {
        action_id: action.id,
        action_name: action.action_name,
        action_slug: action.action_slug,
        provider_id: action.provider_id,
        provider_name: provider.name,
        logo_url: provider.logo_url
      };
    });
  } catch (error) {
    console.error('Error fetching actions by IDs:', error);
    return [];
  }
};

export const createFlow = async (flowRequest: CreateFlowRequest): Promise<string> => {
  try {
    const { data: { user } } = await supabase.auth.getUser();
    
    if (!user) {
      throw new Error('Not authenticated');
    }
    
    if (flowRequest.status === 'Active') {
      const limitCheck = await canUserCreateFlow(1);
      if (!limitCheck.allowed) {
        throw new Error(limitCheck.reason || 'Flow limit exceeded for your current plan');
      }
    }
    
    const { data: newFlow, error: flowError } = await supabase
      .from('user_flows')
      .insert({
        name: flowRequest.name || "New Flow",
        description: flowRequest.description,
        plain_description: flowRequest.plain_description,
        status: flowRequest.status || 'Draft',
        is_shared: false,
        is_template: flowRequest.is_template || false,
        user_id: user.id
      })
      .select('id')
      .single();
    
    if (flowError) throw flowError;
    
    const flowId = newFlow.id;
    
    if (flowRequest.actions && flowRequest.actions.length > 0) {
      const actionsToInsert = flowRequest.actions.map(actionId => ({
        flow_id: flowId,
        action_id: actionId
      }));
      
      const { error: actionsError } = await supabase
        .from('flow_actions')
        .insert(actionsToInsert);
      
      if (actionsError) throw actionsError;
    }
    
    return flowId;
  } catch (error) {
    console.error('Error creating flow:', error);
    throw error;
  }
};

export const updateFlow = async (flowData: UpdateFlowRequest): Promise<void> => {
  try {
    const { data: { user } } = await supabase.auth.getUser();
    
    if (!user) {
      throw new Error('Not authenticated');
    }
    
    const updateObject: any = {};
    if (flowData.name) updateObject.name = flowData.name;
    if (flowData.description) updateObject.description = flowData.description;
    if (flowData.plain_description !== undefined) updateObject.plain_description = flowData.plain_description;
    if (flowData.status) updateObject.status = flowData.status;
    if (flowData.is_shared !== undefined) updateObject.is_shared = flowData.is_shared;
    
    if (Object.keys(updateObject).length > 0) {
      const { error: flowError } = await supabase
        .from('user_flows')
        .update(updateObject)
        .eq('id', flowData.id)
        .eq('user_id', user.id);
      
      if (flowError) throw flowError;
    }
    
    if (flowData.actions) {
      const { error: deleteError } = await supabase
        .from('flow_actions')
        .delete()
        .eq('flow_id', flowData.id);
      
      if (deleteError) throw deleteError;
      
      if (flowData.actions.length > 0) {
        const actionsToInsert = flowData.actions.map(actionId => ({
          flow_id: flowData.id,
          action_id: actionId
        }));
        
        const { error: insertError } = await supabase
          .from('flow_actions')
          .insert(actionsToInsert);
        
        if (insertError) throw insertError;
      }
    }
  } catch (error) {
    console.error('Error updating flow:', error);
    throw error;
  }
};

export const deleteFlow = async (flowId: string): Promise<void> => {
  try {
    const { data: { user } } = await supabase.auth.getUser();
    
    if (!user) {
      throw new Error('Not authenticated');
    }
    
    const { error: actionsError } = await supabase
      .from('flow_actions')
      .delete()
      .eq('flow_id', flowId);
    
    if (actionsError) throw actionsError;
      
    const { error: flowError } = await supabase
      .from('user_flows')
      .delete()
      .eq('id', flowId)
      .eq('user_id', user.id);
    
    if (flowError) throw flowError;
  } catch (error) {
    console.error('Error deleting flow:', error);
    throw error;
  }
};

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
      .select('provider_id, provider_name, action_slug, input_schema, examples, logo_url')
      .eq('user_id', queryUserId);

    if (error) throw error;
    return { data: data || [], error: null };
  } catch (error) {
    console.error('Error fetching actions for flow:', error);
    return { data: [], error };
  }
}

export const updateFlowStatus = async (flowId: string, status: FlowStatus): Promise<void> => {
  try {
    const { data: { user } } = await supabase.auth.getUser();
    
    if (!user) {
      throw new Error('Not authenticated');
    }
    
    if (status === 'Active') {
      const limitCheck = await canUserCreateFlow(1);
      if (!limitCheck.allowed) {
        throw new Error(limitCheck.reason || 'Active flow limit exceeded for your current plan');
      }
    }
    
    const { error } = await supabase
      .from('user_flows')
      .update({ status })
      .eq('id', flowId)
      .eq('user_id', user.id);
    
    if (error) throw error;
  } catch (error) {
    console.error('Error updating flow status:', error);
    throw error;
  }
};

export const extractActionsFromHTML = (html: string, availableActions: ProviderAction[]): string[] => {
  try {
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');
    const actionElements = doc.querySelectorAll('.action-item');
    
    const actionIds: string[] = [];
    
    actionElements.forEach(element => {
      const providerName = element.getAttribute('data-provider');
      const actionSlug = element.getAttribute('data-action');
      
      
      if (providerName && actionSlug) {
        const normalizedProviderName = providerName.toLowerCase().trim();
        const normalizedActionSlug = actionSlug.trim();
        
        const matchingAction = availableActions.find(action => 
          action.provider_name.toLowerCase().trim() === normalizedProviderName && 
          action.action_slug === normalizedActionSlug
        );
        
        if (matchingAction && matchingAction.action_id) {
          actionIds.push(matchingAction.action_id);
        }
      }
    });
    
    return Array.from(new Set(actionIds));
  } catch (error) {
    console.error('Error extracting actions from HTML:', error);
    return [];
  }
};

export const extractTextFromHTML = (html: string): string => {
  try {
    const spacedHtml = html
      .replace(/<\/(p|div|h[1-6]|li|ul|ol|blockquote|pre|table|tr|td|th)>/gi, ' </$1> ')
      .replace(/<(p|div|h[1-6]|li|ul|ol|blockquote|pre|table|tr|td|th)[^>]*>/gi, ' <$1> ')
      .replace(/\s{2,}/g, ' ');
      
    const parser = new DOMParser();
    const doc = parser.parseFromString(spacedHtml, 'text/html');
    const text = doc.body.textContent || '';
    return text.trim();
  } catch (error) {
    console.error('Error extracting text from HTML:', error);
    return '';
  }
};

export const saveFlowWithExtractedActions = async (
  flowData: {
    name: string;
    html: string;
  }, 
  availableActions: ProviderAction[]
): Promise<string> => {
  try {
    const actionIds = extractActionsFromHTML(flowData.html, availableActions);
    const plainText = extractTextFromHTML(flowData.html);
    
    const createRequest: CreateFlowRequest = {
      name: flowData.name,
      description: flowData.html,
      plain_description: plainText,
      actions: actionIds,
      status: 'Draft'
    };
    
    return await createFlow(createRequest);
  } catch (error) {
    console.error('Error saving flow with extracted actions:', error);
    throw error;
  }
};

export const updateFlowWithExtractedActions = async (
  flowId: string,
  flowData: {
    name: string;
    html: string;
  },
  availableActions: ProviderAction[]
): Promise<void> => {
  try {
    const actionIds = extractActionsFromHTML(flowData.html, availableActions);
    const plainText = extractTextFromHTML(flowData.html);
    
    const updateRequest: UpdateFlowRequest = {
      id: flowId,
      name: flowData.name,
      description: flowData.html,
      plain_description: plainText,
      actions: actionIds
    };
    
    await updateFlow(updateRequest);
  } catch (error) {
    console.error('Error updating flow with extracted actions:', error);
    throw error;
  }
};

export const cloneFlow = async (flowId: string): Promise<string> => {
  try {
    const { data: { user } } = await supabase.auth.getUser();
    
    if (!user) {
      throw new Error('Not authenticated');
    }
    
    // 1. Fetch the flow to be cloned
    const { data: flowToClone, error: flowError } = await supabase
      .from('user_flows')
      .select('*')
      .eq('id', flowId)
      .single();
    
    if (flowError) throw flowError;
    
    // 2. Fetch actions associated with the flow
    const { data: flowActions, error: actionsError } = await supabase
      .from('flow_actions')
      .select('action_id')
      .eq('flow_id', flowId);
    
    if (actionsError) throw actionsError;
    
    const actionIds = flowActions?.map(item => item.action_id) || [];
    
    // Create new flow as a copy
    const { data: newFlow, error: createError } = await supabase
      .from('user_flows')
      .insert({
        name: `${flowToClone.name} (Copy)`,
        description: flowToClone.description,
        plain_description: flowToClone.plain_description,
        status: 'Draft',
        is_shared: false,
        user_id: user.id
      })
      .select('id')
      .single();
    
    if (createError) throw createError;
    
    const newFlowId = newFlow.id;
    
    if (actionIds.length > 0) {
      const actionsToInsert = actionIds.map(actionId => ({
        flow_id: newFlowId,
        action_id: actionId
      }));
      
      const { data, error: insertError } = await supabase
        .from('flow_actions')
        .insert(actionsToInsert);
      if (insertError) throw insertError;
    }
    
    return newFlowId;
  } catch (error) {
    console.error('Error cloning flow:', error);
    throw error;
  }
};

export const getPublicTemplates = async (): Promise<UserFlow[]> => {
  try {
    const { data, error } = await supabase
      .from('user_flows')
      .select('*')
      .eq('is_template', true)
      .eq('is_shared', true);
    
    if (error) throw error;
    return data || [];
  } catch (error) {
    console.error('Error fetching public templates:', error);
    throw error;
  }
};

export const getTemplateById = async (flowId: string): Promise<UserFlow | null> => {
  try {
    const { data, error } = await supabase
      .from('user_flows')
      .select('*')
      .eq('id', flowId)
      .eq('is_template', true)
      .eq('is_shared', true)
      .single();
    
    if (error) {
      if (error.code === 'PGRST116') return null;
      throw error;
    }
    return data;
  } catch (error) {
    console.error('Error fetching template:', error);
    return null;
  }
};

export const getTemplateActions = async (templateId: string): Promise<ProviderAction[]> => {
  try {
    const { data: templateData, error: templateError } = await supabase
      .from('user_flows')
      .select('is_template, is_shared')
      .eq('id', templateId)
      .single();
    
    if (templateError) throw templateError;
    
    if (!templateData || !templateData.is_template || !templateData.is_shared) {
      return [];
    }
    
    const { data: actionData, error: actionError } = await supabase
      .from('flow_actions')
      .select('action_id')
      .eq('flow_id', templateId);
    
    if (actionError) throw actionError;
    
    const actionIds = actionData?.map(item => item.action_id) || [];
    
    if (actionIds.length === 0) {
      return [];
    }
    
    const { data: actions, error } = await supabase
      .from('provider_actions')
      .select('id, action_name, action_slug, provider_id')
      .in('id', actionIds);
    
    if (error) throw error;
    
    const providerIds = Array.from(new Set(actions?.map(item => item.provider_id) || []));
    
    if (providerIds.length === 0) {
      return [];
    }
    
    const { data: providersData, error: providersError } = await supabase
      .from('providers')
      .select('id, name, logo_url')
      .in('id', providerIds);
    
    if (providersError) throw providersError;
    
    return (actions || []).map(action => {
      const provider = providersData?.find(p => p.id === action.provider_id) || { name: '', logo_url: '' };
      return {
        action_id: action.id,
        action_name: action.action_name,
        action_slug: action.action_slug,
        provider_id: action.provider_id,
        provider_name: provider.name,
        logo_url: provider.logo_url,
        user_id: ''
      };
    });
  } catch (error) {
    console.error('Error fetching template actions:', error);
    return [];
  }
};