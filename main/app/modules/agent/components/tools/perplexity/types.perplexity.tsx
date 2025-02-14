export interface PerplexityMessage {
    role: 'system' | 'user' | 'assistant';
    content: string;
  }
  
  export interface PerplexityChoice {
    index: number;
    finish_reason: string;
    message: PerplexityMessage;
    delta: {
      role: string;
      content: string;
    };
  }
  
  export interface PerplexityUsage {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  }
  
  export interface PerplexityResponse {
    id: string;
    model: string;
    object: string;
    created: number;
    citations: string[];
    choices: PerplexityChoice[];
    usage: PerplexityUsage;
  }