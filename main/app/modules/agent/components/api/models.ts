import { createOpenRouter } from '@openrouter/ai-sdk-provider';
import { createAnthropic } from '@ai-sdk/anthropic';
import { createOpenAI } from '@ai-sdk/openai';

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

export const AI_MODELS = {
  'gpt-4.1-mini': {
    id: 'gpt-4.1-mini',
    name: 'GPT-4.1 Mini',
    provider: 'openrouter' as const,
    originalProvider: 'openai' as const,
    modelId: 'openai/gpt-4.1-mini',
    directModelId: 'gpt-4.1-mini',
    maxTokens: 128000,
    isDefault: true,
    isPremium: false
  },
  'gpt-4.1': {
    id: 'gpt-4.1',
    name: 'GPT-4.1',
    provider: 'openrouter' as const,
    originalProvider: 'openai' as const,
    modelId: 'openai/gpt-4.1',
    directModelId: 'gpt-4.1',
    isDefault: false,
    isPremium: true
  },
  'claude-3-7-sonnet-20240229': {
    id: 'claude-3-7-sonnet-20240229',
    name: 'Claude 3.7',
    provider: 'openrouter' as const,
    originalProvider: 'anthropic' as const,
    modelId: 'anthropic/claude-3.7-sonnet',
    directModelId: 'claude-3-7-sonnet-20250219',
    isDefault: false,
    isPremium: true
  },
  'claude-3-5-sonnet-20240620': {
    id: 'claude-3-5-sonnet-20240620',
    name: 'Claude 3.5',
    provider: 'openrouter' as const,
    originalProvider: 'anthropic' as const,
    modelId: 'anthropic/claude-3.5-sonnet',
    directModelId: 'claude-3-5-sonnet-20241022',
    maxTokens: 100000,
    isDefault: false,
    isPremium: true
  },
  'gemini-2-5-flash': {
    id: 'gemini-2-5-flash',
    name: 'Gemini 2.5 Flash',
    provider: 'openrouter' as const,
    originalProvider: 'gemini' as const,
    modelId: 'google/gemini-2.5-flash-preview',
    directModelId: 'gemini-2.5-flash',
    maxTokens: 1048576,
    isDefault: false,
    isPremium: true
  },
  'gemini-2-5-pro': {
    id: 'gemini-2-5-pro',
    name: 'Gemini 2.5 Pro',
    provider: 'openrouter' as const,
    originalProvider: 'gemini' as const,
    modelId: 'google/gemini-2.5-pro-preview',
    directModelId: 'gemini-2.5-pro',
    maxTokens: 1048576,
    isDefault: false,
    isPremium: true
  }
} as const;

export type ModelId = keyof typeof AI_MODELS;
export const DEFAULT_MODEL: ModelId = 'gpt-4.1-mini';

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

const OPENAI_API_KEY = process.env.OPENAI_API_KEY;
const ANTHROPIC_API_KEY = process.env.ANTHROPIC_API_KEY;
const OPENROUTER_API_KEY = process.env.OPENROUTER_API_KEY;

export function initializeModel(modelId: ModelId, settings?: ApiKeySettings) {
  const model = getModelWithEffectiveProvider(modelId, settings);
  const provider = model.provider;
  
  const providerModelId = (provider !== 'openrouter') ? model.directModelId : model.modelId;
  
  const useCustomApiKey = settings?.api_key_enabled && settings?.api_key_provider_name === model.originalProvider;
  const customApiKey = useCustomApiKey ? settings?.api_key : undefined;
  
  switch (provider) {
    case 'openai':
      return createOpenAI({
        apiKey: customApiKey || OPENAI_API_KEY || '',
      })(providerModelId);
      
    case 'anthropic':
      return createAnthropic({
        apiKey: customApiKey || ANTHROPIC_API_KEY || '',
      })(providerModelId);
      
    case 'openrouter':
    default:
      return createOpenRouter({
        apiKey: OPENROUTER_API_KEY || '',
      })(providerModelId);
  }
}
