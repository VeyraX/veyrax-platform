import React, { useState, useEffect, useCallback, memo } from "react";
import { Separator } from "@/components/ui/separator";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { AI_MODELS, ModelId, getDefaultModel } from "../../agent/components/api/models";
import { toast } from "sonner";
import { Loader2 } from "lucide-react";
import { UserPlaygroundSettings, UserAvailableModels } from "../api/types.settings";
import { Skeleton } from "@/components/ui/skeleton";
import { Switch } from "@/components/ui/switch";
import { validateApiKey } from "../api/api.settings";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { CheckCircle, XCircle, AlertCircle } from "lucide-react";
import { setCacheItem, CacheStore } from "@/lib/utils/index-db";
import { createClient } from '@/lib/utils/supabase/client';

interface PlaygroundSettingsProps {
  playgroundSettings: UserPlaygroundSettings | null;
  availableModels: UserAvailableModels | null;
  isLoading: boolean;
  onSave: (data: {
    modelId: ModelId;
    prompt: string;
    provider: string;
    apiKey: string;
    apiKeyEnabled: boolean;
  }) => Promise<void>;
  onApiKeySettingsChange: (data: {
    api_key_enabled: boolean;
    api_key_provider_name: string;
  }) => void;
}

function PlaygroundSettings({
  playgroundSettings,
  availableModels,
  isLoading,
  onSave,
  onApiKeySettingsChange,
}: PlaygroundSettingsProps) {
  const defaultModel = getDefaultModel().id as ModelId;
  
  const [selectedModelId, setSelectedModelId] = useState<ModelId>(defaultModel);
  const [prompt, setPrompt] = useState<string>("You are a helpful AI assistant.");
  const [provider, setProvider] = useState<string>("openai");
  const [apiKey, setApiKey] = useState<string>("");
  const [apiKeyEnabled, setApiKeyEnabled] = useState<boolean>(false);
  const [isSaving, setIsSaving] = useState(false);
  const [hasSettingsChanged, setHasSettingsChanged] = useState(false);
  const [apiKeyStatus, setApiKeyStatus] = useState<'idle' | 'validating' | 'valid' | 'invalid' | 'error'>('idle');
  const [apiKeyError, setApiKeyError] = useState<string>("");

  useEffect(() => {
    if (!playgroundSettings) return;
    
    setSelectedModelId(playgroundSettings.ai_model as ModelId || defaultModel);
    setPrompt(playgroundSettings.agent_prompt || "You are a helpful AI assistant.");
    setProvider(playgroundSettings.api_key_provider_name || "openai");
    setApiKey(playgroundSettings.api_key || "");
    setApiKeyEnabled(!!playgroundSettings.api_key_enabled);
    
    setHasSettingsChanged(false);
  }, [playgroundSettings, defaultModel]);

  useEffect(() => {
    if (!playgroundSettings) return;
    
    const settingsChanged = 
      selectedModelId !== playgroundSettings.ai_model ||
      prompt !== playgroundSettings.agent_prompt ||
      provider !== playgroundSettings.api_key_provider_name ||
      apiKey !== playgroundSettings.api_key ||
      apiKeyEnabled !== playgroundSettings.api_key_enabled;
    
    setHasSettingsChanged(settingsChanged);
  }, [
    playgroundSettings,
    selectedModelId,
    prompt,
    provider,
    apiKey,
    apiKeyEnabled
  ]);

  const handleModelSelect = async (modelId: ModelId) => {
    setSelectedModelId(modelId);
    
    if (availableModels) {
      const supabase = createClient();
      const { data: { user } } = await supabase.auth.getUser();
      const userId = user?.id || 'anonymous';
      
      await setCacheItem(CacheStore.AVAILABLE_MODELS, 'availableModels', userId, {
        models: availableModels.models,
        isPremiumAllowed: availableModels.isPremiumAllowed,
        defaultModelId: modelId
      });
    }
  };

  const handleProviderApiKeyChange = useCallback(() => {
    if (apiKeyEnabled) {
      onApiKeySettingsChange({
        api_key_enabled: apiKeyEnabled,
        api_key_provider_name: provider
      });
    }
  }, [apiKeyEnabled, provider, onApiKeySettingsChange]);

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      handleProviderApiKeyChange();
    }, 500);
    
    return () => clearTimeout(timeoutId);
  }, [handleProviderApiKeyChange]);

  const handleApiKeyChange = (value: string) => {
    setApiKey(value);
    setApiKeyStatus('idle');
    setApiKeyError("");
  };

  const validateCurrentApiKey = async () => {
    if (!apiKeyEnabled || !apiKey) return true;
    
    setApiKeyStatus('validating');
    setApiKeyError("");
    
    try {
      const validation = await validateApiKey(provider, apiKey);
      
      if (validation.valid) {
        setApiKeyStatus('idle');
        return true;
      } else {
        setApiKeyStatus('invalid');
        setApiKeyError(validation.error || "Invalid API key");
        return false;
      }
    } catch (error) {
      setApiKeyStatus('error');
      setApiKeyError("Failed to validate API key");
      return false;
    }
  };

  const handleSave = async () => {
    if (!hasSettingsChanged) {
      return;
    }
    
    setIsSaving(true);
    
    // Validate API key if enabled
    if (apiKeyEnabled && apiKey) {
      const isValid = await validateCurrentApiKey();
      if (!isValid) {
        setIsSaving(false);
        return;
      }
    }
    
    try {
      await onSave({
        modelId: selectedModelId,
        prompt,
        provider,
        apiKey,
        apiKeyEnabled,
      });
      
      setHasSettingsChanged(false);
    } catch (error) {
      console.error("Error saving playground settings:", error);
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div>
          <Skeleton className="h-8 w-64 mb-2" />
          <Skeleton className="h-4 w-full max-w-md" />
        </div>
        
        <Separator />
        
        <div>
          <Skeleton className="h-6 w-32 mb-2" />
          <Skeleton className="h-4 w-full max-w-lg mb-5" />
          <Skeleton className="h-32 w-full" />
        </div>
        
        <Separator />
        
        <div>
          <Skeleton className="h-6 w-28 mb-2" />
          <Skeleton className="h-4 w-full max-w-lg mb-5" />
          <Skeleton className="h-10 w-full" />
        </div>
        
        <Separator />
        
        <div>
          <div className="flex justify-between items-center mb-4">
            <div>
              <Skeleton className="h-6 w-40 mb-2" />
              <Skeleton className="h-4 w-full max-w-md" />
            </div>
            <div className="flex items-center space-x-2">
              <Skeleton className="h-5 w-10" />
              <Skeleton className="h-5 w-16" />
            </div>
          </div>
        </div>
        
        <div className="flex justify-end mt-6">
          <Skeleton className="h-10 w-28" />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold tracking-tight">Playground</h2>
        <p className="text-sm text-muted-foreground">
          Configure your AI settings and custom API keys.
        </p>
      </div>

      <Separator />

      <div>
        <h3 className="text-lg font-medium">Agent Prompt</h3>
        <p className="text-sm text-muted-foreground mb-4">
          Set a default system prompt for the AI assistant.
        </p>
        
        <Textarea
          placeholder="You are a helpful assistant..."
          className="min-h-[150px] font-mono text-sm"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
        />
      </div>

      <Separator />

      <div>
        <h3 className="text-lg font-medium">Default AI Model</h3>
        <p className="text-sm text-muted-foreground mb-4">
          Select the AI model to use for your conversations.
        </p>
        
        <div className="mb-4">
          <Select
            value={selectedModelId}
            onValueChange={(value) => handleModelSelect(value as ModelId)}
          >
            <SelectTrigger className="w-full">
              <SelectValue placeholder="Select model" />
            </SelectTrigger>
            <SelectContent>
              {Object.entries(AI_MODELS).map(([id, model]) => {
                const isAvailable = !availableModels || 
                  availableModels.models.includes(id);
                const isPremium = model.isPremium && (!availableModels || !availableModels.isPremiumAllowed);
                
                return (
                  <SelectItem 
                    key={id} 
                    value={id}
                    disabled={!isAvailable}
                  >
                    {model.name}
                  </SelectItem>
                );
              })}
            </SelectContent>
          </Select>
        </div>
      </div>

      <Separator />

      <div>
        <div className="flex justify-between items-center mb-4">
          <div>
            <h3 className="text-lg font-medium">Custom API Key</h3>
            <p className="text-sm text-muted-foreground">
              Use your own API keys for additional capabilities.
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <Switch
              id="api-key-enabled"
              checked={apiKeyEnabled}
              onCheckedChange={setApiKeyEnabled}
            />
          </div>
        </div>
        
        {apiKeyEnabled && (
          <div className="grid gap-4">
            {apiKeyStatus !== 'idle' && (
              <div>
                {apiKeyStatus === 'validating' && (
                  <Alert className="bg-blue-50 dark:bg-blue-950 border-blue-200 dark:border-blue-900">
                    <div className="flex items-center">
                      <Loader2 className="h-4 w-4 text-blue-500 animate-spin mr-2" />
                      <AlertDescription className="text-blue-700 dark:text-blue-400">
                        Validating API key...
                      </AlertDescription>
                    </div>
                  </Alert>
                )}
                
                {(apiKeyStatus === 'invalid' || apiKeyStatus === 'error') && (
                  <Alert variant="destructive">
                    <div className="flex items-center">
                      <XCircle className="h-4 w-4 mr-2" />
                      <AlertDescription>
                        {apiKeyError}
                      </AlertDescription>
                    </div>
                  </Alert>
                )}
              </div>
            )}

            <div className="grid gap-2">
              <Label htmlFor="provider">Provider</Label>
              <Select 
                value={provider} 
                onValueChange={setProvider}
              >
                <SelectTrigger id="provider">
                  <SelectValue placeholder="Select provider" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="openai">OpenAI</SelectItem>
                  <SelectItem value="anthropic">Anthropic</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="grid gap-2">
              <Label htmlFor="api-key">API Key</Label>
              <div className="flex gap-2">
                <Input
                  id="api-key"
                  type="password"
                  placeholder={`Enter your ${provider === 'openai' ? 'OpenAI' : 'Anthropic'} API key`}
                  className="font-mono flex-1"
                  value={apiKey}
                  onChange={(e) => handleApiKeyChange(e.target.value)}
                />
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="flex justify-end mt-6">
        <Button
          onClick={handleSave}
          disabled={isSaving || !hasSettingsChanged}
        >
          {isSaving ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : "Save Changes"}
        </Button>
      </div>
    </div>
  );
}

export default memo(PlaygroundSettings); 