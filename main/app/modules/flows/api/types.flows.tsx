export interface ProviderAction {
    provider_name: string;
    provider_id: string;
    logo_url: string;
    action_name: string;
    action_slug: string;
    action_id: string;
    user_id: string;
  }

export type FlowStatus = 'Draft' | 'Active';

export interface UserFlow {
  id: string;
  name: string;
  description: string;
  plain_description?: string;
  status: FlowStatus;
  is_shared: boolean;
  user_id: string;
  created_at?: string;
  updated_at?: string;
}

export interface FlowAction {
  flow_id: string;
  action_id: string;
}

export interface CreateFlowRequest {
  name: string;
  description: string;
  plain_description?: string;
  status?: FlowStatus;
  actions?: string[]; // Array of action_ids
}

export interface UpdateFlowRequest {
  id: string;
  name?: string;
  description?: string;
  plain_description?: string;
  status?: FlowStatus;
  is_shared?: boolean;
  actions?: string[]; // Array of action_ids
}