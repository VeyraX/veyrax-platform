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
  actions?: string[];
}

export interface FlowSchedule {
  type: 'recurring' | 'once';
  recurrence?: {
    dayOfWeek?: 0 | 1 | 2 | 3 | 4 | 5 | 6;
    dayOfMonth?: number;
    time: string;  
    timezone: string;
  };
  oneTime?: {
    datetime: string;  
    timezone: string;
  };
}

export interface UserFlowSchedule {
  flow_id: string;
  schedule: FlowSchedule;
}

export type FlowRunStatus = 'pending' | 'running' | 'completed' | 'failed';

export interface ToolInvocation {
  args: Record<string, any>;
  toolName: string;
  toolCallId: string;
  result?: Record<string, any>;
  state?: string;
  step?: number;
  metadata?: {
    toolInvocations: ToolInvocation[];
    finishReason: string;
    isServiceAccount: boolean;
  };
}

export interface FlowRunPart {
  type: 'text' | 'tool-invocation';
  text?: string;
  toolInvocation?: ToolInvocation;
}

export interface FlowRunPayload {
  parts: FlowRunPart[];
  sender: string;
  metadata: {
    finishReason: string;
    toolInvocations: ToolInvocation[];
    isServiceAccount: boolean;
  };
  message_id: string;
  message_text: string;
}

export interface UserFlowRun {
  id: string;
  flow_id: string;
  run_status: FlowRunStatus;
  run_at: string;
  completed_at?: string;
  payload?: FlowRunPayload;
}