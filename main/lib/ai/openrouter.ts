import { createOpenRouter } from '@openrouter/ai-sdk-provider';

// Every model call goes through OpenRouter, so OPENROUTER_API_KEY is the only key needed.
// Model IDs: https://openrouter.ai/models. Server-side only.

export const OPENROUTER_BASE_URL = 'https://openrouter.ai/api/v1';

// Flow builder and flow runs (tool-using agent)
export const AGENT_MODEL = process.env.OPENROUTER_AGENT_MODEL || 'anthropic/claude-sonnet-5.5';
// Short tasks: chat titles, suggestions
export const FAST_MODEL = process.env.OPENROUTER_FAST_MODEL || 'openai/gpt-6-luna';
// Same vectors as OpenAI's text-embedding-3-small, so existing vector indexes stay valid
export const EMBEDDING_MODEL = 'openai/text-embedding-3-small';
export const TRANSCRIPTION_MODEL = 'openai/whisper-large-v3-turbo';

export const openrouterHeaders = {
  'HTTP-Referer': process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000',
  'X-Title': 'Veyrax',
};

export const openrouter = createOpenRouter({
  apiKey: process.env.OPENROUTER_API_KEY || '',
  headers: openrouterHeaders,
});
