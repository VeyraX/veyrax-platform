import { createAnthropic } from '@ai-sdk/anthropic';
import { createOpenAI } from '@ai-sdk/openai';
import { openrouter } from '@/lib/ai/openrouter';

export interface AIModel {
  id: string;
  name: string;
  description?: string;
  provider: 'openai' | 'anthropic' | 'gemini' | 'openrouter';
  originalProvider: 'openai' | 'anthropic' | 'gemini';
  modelId: string;
  directModelId: string;
  maxTokens: number;
  isDefault?: boolean;
  enableReasoning?: boolean;
  isPremium?: boolean;
}

// Chat models offered in the playground, served through OpenRouter (https://openrouter.ai/models).
// directModelId is used when a user brings their own OpenAI / Anthropic key in settings.
export const AI_MODELS = {
  'gpt-6-luna': {
    id: 'gpt-6-luna',
    name: 'GPT-6 Luna',
    provider: 'openrouter' as const,
    originalProvider: 'openai' as const,
    modelId: 'openai/gpt-6-luna',
    directModelId: 'gpt-6-luna',
    maxTokens: 1050000,
    isDefault: true,
    isPremium: false
  },
  'claude-haiku-5.5': {
    id: 'claude-haiku-5.5',
    name: 'Claude Haiku 5.5',
    provider: 'openrouter' as const,
    originalProvider: 'anthropic' as const,
    modelId: 'anthropic/claude-haiku-5.5',
    directModelId: 'claude-haiku-5-5',
    maxTokens: 1000000,
    isDefault: false,
    isPremium: false
  },
  'gpt-6.1-sol': {
    id: 'gpt-6.1-sol',
    name: 'GPT-6.1 Sol',
    provider: 'openrouter' as const,
    originalProvider: 'openai' as const,
    modelId: 'openai/gpt-6.1-sol',
    directModelId: 'gpt-6.1-sol',
    maxTokens: 1050000,
    isDefault: false,
    isPremium: true
  },
  'claude-sonnet-5.5': {
    id: 'claude-sonnet-5.5',
    name: 'Claude Sonnet 5.5',
    provider: 'openrouter' as const,
    originalProvider: 'anthropic' as const,
    modelId: 'anthropic/claude-sonnet-5.5',
    directModelId: 'claude-sonnet-5-5',
    maxTokens: 1000000,
    isDefault: false,
    isPremium: true
  },
  'claude-opus-5.5': {
    id: 'claude-opus-5.5',
    name: 'Claude Opus 5.5',
    provider: 'openrouter' as const,
    originalProvider: 'anthropic' as const,
    modelId: 'anthropic/claude-opus-5.5',
    directModelId: 'claude-opus-5-5',
    maxTokens: 1000000,
    isDefault: false,
    isPremium: true
  },
  'gemini-3.8-flash': {
    id: 'gemini-3.8-flash',
    name: 'Gemini 3.8 Flash',
    provider: 'openrouter' as const,
    originalProvider: 'gemini' as const,
    modelId: 'google/gemini-3.8-flash',
    directModelId: 'gemini-3.8-flash',
    maxTokens: 1048576,
    isDefault: false,
    isPremium: true
  }
} as const;

export type ModelId = keyof typeof AI_MODELS;
export const DEFAULT_MODEL: ModelId = 'gpt-6-luna';

export const availableModels = Object.values(AI_MODELS);

export const getDefaultModel = (): AIModel => {
  return AI_MODELS[DEFAULT_MODEL];
};

export interface ApiKeySettings {
  api_key_enabled?: boolean;
  api_key_provider_name?: string;
  api_key?: string;
}

export function getEffectiveModelProvider(
  modelId: ModelId,
  settings?: ApiKeySettings
): 'openrouter' | 'openai' | 'anthropic' | 'gemini' {
  const model = AI_MODELS[modelId];
  
  if (settings?.api_key_enabled && 
      settings.api_key_provider_name === model.originalProvider) {
    return model.originalProvider;
  }
  
  return 'openrouter';
}

export function getModelWithEffectiveProvider(
  modelId: ModelId, 
  settings?: ApiKeySettings
): AIModel {
  const modelCopy = JSON.parse(JSON.stringify(AI_MODELS[modelId])) as AIModel;
  const effectiveProvider = getEffectiveModelProvider(modelId, settings);
  
  modelCopy.provider = effectiveProvider;
  
  return modelCopy;
}

export function initializeModel(modelId: ModelId, settings?: ApiKeySettings) {
  const model = getModelWithEffectiveProvider(modelId, settings);
  const provider = model.provider;
  
  const useCustomApiKey = settings?.api_key_enabled && settings?.api_key_provider_name === model.originalProvider;
  const customApiKey = useCustomApiKey ? settings?.api_key : undefined;
  
  switch (provider) {
    case 'openai':
      // GPT-6 models need the Responses API for tool calls
      return createOpenAI({ apiKey: customApiKey || '' }).responses(model.directModelId);

    case 'anthropic':
      return createAnthropic({ apiKey: customApiKey || '' })(model.directModelId);

    default:
      return openrouter(model.modelId);
  }
}
