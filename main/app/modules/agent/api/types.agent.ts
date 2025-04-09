export interface Chat {
    id: string
    created_at: string
    updated_at: string | null
    user_id: string
    name: string
    is_shared: boolean | null
  }
  
  export interface CreateChatPayload {
    name: string
  }

export interface ChatMessage {
  message_id: string;
  chat_id: string;
  sender: 'user' | 'assistant';
  message_text: string;
  image_url?: string;
  created_at: string;
  is_accurate?: boolean;
  parts?: Array<{
    type: 'text' | 'tool-call' | 'tool-result';
    text?: string;
    toolCall?: {
      toolCallId: string;
      toolName: string;
      args: any;
    };
    toolResult?: {
      toolCallId: string;
      toolName: string;
      result: string;
      isError?: boolean;
    };
  }>;
  metadata?: {
    toolInvocations?: Array<{
      toolCallId: string;
      toolName: string;
      args: any;
      state: 'partial' | 'called' | 'completed' | 'error';
      result?: string;
    }>;
    finishReason?: 'stop' | 'length' | 'tool_calls' | 'error' | null;
  };
}

export interface CreateChatMessagePayload {
  message_id: string;
  chat_id: string;
  sender: 'user' | 'assistant';
  message_text: string;
  image_url?: string;
  parts?: Array<{
    type: 'text' | 'tool-invocation';
    text?: string;
    toolInvocation?: {
      toolCallId: string;
      toolName: string;
      args: any;
      result?: string;
    };
  }>;
  metadata?: {
    toolInvocations?: Array<{
      toolCallId: string;
      toolName: string;
      args: any;
      state: string;
      result?: string;
    }>;
    finishReason?: string | null;
  };
}

export interface CreateFlowMessagePayload {
  message_id: string;
  flow_id: string | null;
  sender: 'user' | 'assistant';
  message_text: string;
  parts?: Array<{
    type: 'text' | 'tool-invocation';
    text?: string;
    toolInvocation?: {
      toolCallId: string;
      toolName: string;
      args: any;
      result?: string;
    };
  }>;
  metadata?: {
    toolInvocations?: Array<{
      toolCallId: string;
      toolName: string;
      args: any;
      state: string;
      result?: string;
    }>;
    finishReason?: string | null;
  };
  type: 'create' | 'test';
}