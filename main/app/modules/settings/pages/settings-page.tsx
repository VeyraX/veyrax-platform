'use client';

import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { UserCircle2, Key, Terminal, CreditCard, FlaskConical } from "lucide-react"
import Link from "next/link"
import AccountSettings from "../components/account-settings"
import ApiKeySettings from "../components/api-key-settings"
import MCPSettings from "../components/mcp-settings"
import BillingSettings from "../components/billing-settings"
import { useState, useEffect } from "react"
import { getUserProfile, getUserApiKey, generateApiKey, revokeApiKey, getUserSubscription, getUserPlaygroundSettings, saveUserPlaygroundSettings, getUserAvailableModels } from "../api/api.settings"
import { UserProfile, UserApiKey, UserSubscription, UserPlaygroundSettings, UserAvailableModels } from "../api/types.settings"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import PlaygroundSettings from "../components/playground-settings"
import { ModelId } from "../../agent/components/api/models"
import { toast } from "sonner"
import { CacheUtils, CACHE_KEYS } from "@/lib/utils/cache-utils"

interface AccountSettingsDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  initialTab?: 'account' | 'api-key' | 'mcp' | 'billing' | 'playground'
}

export function AccountSettingsDialog({ 
  open, 
  onOpenChange, 
  initialTab = 'account' 
}: AccountSettingsDialogProps) {
  const [activeTab, setActiveTab] = useState<'account' | 'api-key' | 'mcp' | 'billing' | 'playground'>(initialTab);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [apiKey, setApiKey] = useState<UserApiKey | null>(null);
  const [subscription, setSubscription] = useState<UserSubscription | null>(null);
  const [playgroundSettings, setPlaygroundSettings] = useState<UserPlaygroundSettings | null>(null);
  const [availableModels, setAvailableModels] = useState<UserAvailableModels | null>(null);
  const [isLoadingProfile, setIsLoadingProfile] = useState(true);
  const [isLoadingApiKey, setIsLoadingApiKey] = useState(true);
  const [isLoadingSubscription, setIsLoadingSubscription] = useState(true);
  const [isLoadingPlaygroundSettings, setIsLoadingPlaygroundSettings] = useState(true);
  const [isLoadingAvailableModels, setIsLoadingAvailableModels] = useState(true);

  useEffect(() => {
    if (open) {
      const fetchInitialData = async () => {
        setIsLoadingProfile(true);
        try {
          const data = await getUserProfile();
          setProfile(data);
        } catch (error) {
          console.error('Error fetching user profile:', error);
        } finally {
          setIsLoadingProfile(false);
        }
      };
      
      fetchInitialData();
    }
  }, [open]);

  useEffect(() => {
    if (open && activeTab === 'api-key' && isLoadingApiKey) {
      const fetchApiKey = async () => {
        try {
          const data = await getUserApiKey();
          setApiKey(data);
        } catch (error) {
          console.error('Error fetching API key:', error);
        } finally {
          setIsLoadingApiKey(false);
        }
      };
      
      fetchApiKey();
    }
  }, [open, activeTab, isLoadingApiKey]);

  useEffect(() => {
    if (open && activeTab === 'billing' && isLoadingSubscription) {
      const fetchSubscription = async () => {
        try {
          const data = await getUserSubscription();
          setSubscription(data);
        } catch (error) {
          console.error('Error fetching subscription:', error);
        } finally {
          setIsLoadingSubscription(false);
        }
      };
      
      fetchSubscription();
    }
  }, [open, activeTab, isLoadingSubscription]);

  useEffect(() => {
    if (open && activeTab === 'playground' && isLoadingPlaygroundSettings) {
      const fetchPlaygroundSettings = async () => {
        try {
          const data = await getUserPlaygroundSettings();
          setPlaygroundSettings(data);
        } catch (error) {
          console.error('Error fetching playground settings:', error);
        } finally {
          setIsLoadingPlaygroundSettings(false);
        }
      };
      
      fetchPlaygroundSettings();
    }
  }, [open, activeTab, isLoadingPlaygroundSettings]);

  useEffect(() => {
    if (open && activeTab === 'playground' && !isLoadingPlaygroundSettings && isLoadingAvailableModels) {
      const fetchAvailableModels = async () => {
        try {
          let data;
          if (playgroundSettings && playgroundSettings.api_key_enabled) {
            data = await getUserAvailableModels({
              api_key_enabled: playgroundSettings.api_key_enabled,
              api_key_provider_name: playgroundSettings.api_key_provider_name
            });
          } else {
            data = await getUserAvailableModels();
          }
          setAvailableModels(data);
        } catch (error) {
          console.error('Error fetching available models:', error);
        } finally {
          setIsLoadingAvailableModels(false);
        }
      };
      
      fetchAvailableModels();
    }
  }, [open, activeTab, playgroundSettings, isLoadingPlaygroundSettings, isLoadingAvailableModels]);

  const handleTabChange = (tab: 'account' | 'api-key' | 'mcp' | 'billing' | 'playground') => {
    setActiveTab(tab);
    
    if (tab === 'api-key' && apiKey === null) {
      setIsLoadingApiKey(true);
    }
    
    if (tab === 'billing' && subscription === null) {
      setIsLoadingSubscription(true);
    }
    
    if (tab === 'playground' && playgroundSettings === null) {
      setIsLoadingPlaygroundSettings(true);
    }
    
    if (tab === 'playground' && availableModels === null) {
      setIsLoadingAvailableModels(true);
    }
  };

  const handleGenerateApiKey = async () => {
    try {
      const newKey = await generateApiKey();
      setApiKey(newKey);
      return newKey;
    } catch (error) {
      console.error('Error generating API key:', error);
      return null;
    }
  };

  const handleRevokeApiKey = async () => {
    try {
      const success = await revokeApiKey();
      if (success) {
        setApiKey(null);
      }
      return success;
    } catch (error) {
      console.error('Error revoking API key:', error);
      return false;
    }
  };

  const handleSavePlaygroundSettings = async (data: {
    modelId: ModelId;
    prompt: string;
    provider: string;
    apiKey: string;
    apiKeyEnabled: boolean;
  }) => {
    try {
      const apiKeySettingsChanged = 
        playgroundSettings && 
        (data.apiKeyEnabled !== playgroundSettings.api_key_enabled || 
         data.provider !== playgroundSettings.api_key_provider_name);
      
      if (playgroundSettings?.api_key_enabled && !data.apiKeyEnabled) {
        CacheUtils.invalidateCache(CACHE_KEYS.AVAILABLE_MODELS);
      }
      
      const result = await saveUserPlaygroundSettings({
        ai_model: data.modelId,
        agent_prompt: data.prompt,
        api_key_provider_name: data.provider,
        api_key: data.apiKey,
        api_key_enabled: data.apiKeyEnabled
      });
      
      if (result) {
        setPlaygroundSettings(result);
        
        if (apiKeySettingsChanged) {
          setTimeout(() => {
            getUserAvailableModels({
              api_key_enabled: data.apiKeyEnabled,
              api_key_provider_name: data.provider
            }).then(newModelsData => {
              setAvailableModels(newModelsData);
              CacheUtils.updateCache(CACHE_KEYS.AVAILABLE_MODELS, newModelsData);
              
              if (result.ai_model && newModelsData.models.length > 0 && 
                  !newModelsData.models.includes(result.ai_model as string)) {
                const newModelId = newModelsData.models[0];
                console.log(`Model ${result.ai_model} no longer available, switching to ${newModelId}`);
                
                saveUserPlaygroundSettings({
                  ...result,
                  ai_model: newModelId as ModelId
                }).then(updatedResult => {
                  if (updatedResult) {
                    setPlaygroundSettings(updatedResult);
                  }
                }).catch(e => {
                  console.error('Error updating model selection:', e);
                });
              }
            }).catch(error => {
              console.error('Error updating available models:', error);
            });
          }, 100);
        }
        
        return result;
      } else {
        throw new Error("Failed to save settings");
      }
    } catch (error) {
      console.error('Error saving playground settings:', error);
      throw error;
    }
  };

  const handleApiKeySettingsChange = async (settings: {
    api_key_enabled: boolean;
    api_key_provider_name: string;
  }) => {
    try {
      const data = await getUserAvailableModels(settings);
      setAvailableModels(data);
    } catch (error) {
      console.error('Error updating available models:', error);
    }
  };

  useEffect(() => {
    if (initialTab) {
      setActiveTab(initialTab);
    }
  }, [initialTab]);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl p-0 h-[80vh] overflow-hidden">
        {/* Mobile view - tabs at the top */}
        <div className="block sm:hidden">
          <div className="p-4 border-b">
            <DialogHeader className="mb-4">
              <DialogTitle className="text-xl font-semibold tracking-tight">Settings</DialogTitle>
            </DialogHeader>
            
            <Tabs value={activeTab} onValueChange={(value) => handleTabChange(value as any)}>
              <TabsList className="grid grid-cols-5 w-full">
                <TabsTrigger value="account" className="flex items-center gap-1.5 text-xs">
                  <UserCircle2 className="h-3.5 w-3.5" />
                  <span className="hidden xs:inline">Account</span>
                </TabsTrigger>
                <TabsTrigger value="billing" className="flex items-center gap-1.5 text-xs">
                  <CreditCard className="h-3.5 w-3.5" />
                  <span className="hidden xs:inline">Billing</span>
                </TabsTrigger>
                <TabsTrigger value="api-key" className="flex items-center gap-1.5 text-xs">
                  <Key className="h-3.5 w-3.5" />
                  <span className="hidden xs:inline">API Key</span>
                </TabsTrigger>
                <TabsTrigger value="mcp" className="flex items-center gap-1.5 text-xs">
                  <Terminal className="h-3.5 w-3.5" />
                  <span className="hidden xs:inline">MCP</span>
                </TabsTrigger>
                <TabsTrigger value="playground" className="flex items-center gap-1.5 text-xs">
                  <FlaskConical className="h-3.5 w-3.5" />
                  <span className="hidden xs:inline">Playground</span>
                </TabsTrigger>
              </TabsList>
            </Tabs>
          </div>
          
          <div className="p-4 overflow-y-auto max-h-[calc(90vh-120px)]">
            {activeTab === 'account' ? (
              <AccountSettings 
                profile={profile} 
                isLoading={isLoadingProfile} 
              />
            ) : activeTab === 'billing' ? (
              <BillingSettings 
                subscriptionInfo={subscription}
                isLoading={isLoadingSubscription}
              />
            ) : activeTab === 'api-key' ? (
              <ApiKeySettings 
                apiKey={apiKey}
                isLoading={isLoadingApiKey}
                onGenerateApiKey={handleGenerateApiKey}
                onRevokeApiKey={handleRevokeApiKey}
              />
            ) : activeTab === 'mcp' ? (
              <MCPSettings 
                apiKey={apiKey}
                onGenerateApiKey={handleGenerateApiKey}
              />
            ) : activeTab === 'playground' ? (
              <PlaygroundSettings 
                playgroundSettings={playgroundSettings}
                isLoading={isLoadingPlaygroundSettings || isLoadingAvailableModels}
                availableModels={availableModels}
                onSave={handleSavePlaygroundSettings}
                onApiKeySettingsChange={handleApiKeySettingsChange}
              />
            ) : (
              <PlaygroundSettings 
                playgroundSettings={playgroundSettings}
                isLoading={isLoadingPlaygroundSettings || isLoadingAvailableModels}
                availableModels={availableModels}
                onSave={handleSavePlaygroundSettings}
                onApiKeySettingsChange={handleApiKeySettingsChange}
              />
            )}
          </div>
        </div>

        {/* Desktop view - original layout */}
        <div className="hidden sm:flex h-full">
          <div className="w-64 border-r p-6">
            <DialogHeader>
              <DialogTitle className="text-2xl font-semibold tracking-tight">Settings</DialogTitle>
              <p className="text-sm text-muted-foreground">Manage your account info.</p>
            </DialogHeader>

            <nav className="space-y-0.5 -ml-3 mt-4">
              <Link
                href="#"
                onClick={(e) => {
                  e.preventDefault();
                  handleTabChange('account');
                }}
                className={`flex items-center gap-1.5 px-2 py-1.5 rounded-md text-sm ${
                  activeTab === 'account' 
                    ? 'bg-secondary text-secondary-foreground' 
                    : 'text-muted-foreground hover:bg-secondary'
                }`}
              >
                <UserCircle2 className="h-3.5 w-3.5" />
                <span>Account</span>
              </Link>
              <Link
                href="#"
                onClick={(e) => {
                  e.preventDefault();
                  handleTabChange('billing');
                }}
                className={`flex items-center gap-1.5 px-2 py-1.5 rounded-md text-sm ${
                  activeTab === 'billing' 
                    ? 'bg-secondary text-secondary-foreground' 
                    : 'text-muted-foreground hover:bg-secondary'
                }`}
              >
                <CreditCard className="h-3.5 w-3.5" />
                <span>Billing</span>
              </Link>
              <Link
                href="#"
                onClick={(e) => {
                  e.preventDefault();
                  handleTabChange('api-key');
                }}
                className={`flex items-center gap-1.5 px-2 py-1.5 rounded-md text-sm ${
                  activeTab === 'api-key' 
                    ? 'bg-secondary text-secondary-foreground' 
                    : 'text-muted-foreground hover:bg-secondary'
                }`}
              >
                <Key className="h-3.5 w-3.5" />
                <span>API Key</span>
              </Link>
              <Link
                href="#"
                onClick={(e) => {
                  e.preventDefault();
                  handleTabChange('mcp');
                }}
                className={`flex items-center gap-1.5 px-2 py-1.5 rounded-md text-sm ${
                  activeTab === 'mcp' 
                    ? 'bg-secondary text-secondary-foreground' 
                    : 'text-muted-foreground hover:bg-secondary'
                }`}
              >
                <Terminal className="h-3.5 w-3.5" />
                <span>MCP & Plugins</span>
              </Link>
              <Link
                href="#"
                onClick={(e) => {
                  e.preventDefault();
                  handleTabChange('playground');
                }}
                className={`flex items-center gap-1.5 px-2 py-1.5 rounded-md text-sm ${
                  activeTab === 'playground' 
                    ? 'bg-secondary text-secondary-foreground' 
                    : 'text-muted-foreground hover:bg-secondary'
                }`}
              >
                <FlaskConical className="h-3.5 w-3.5" />
                <span>Playground</span>
              </Link>
            </nav>
          </div>

          <div className="flex-1 p-6 overflow-y-auto max-h-[80vh]">
            {activeTab === 'account' ? (
              <AccountSettings 
                profile={profile} 
                isLoading={isLoadingProfile} 
              />
            ) : activeTab === 'billing' ? (
              <BillingSettings 
                subscriptionInfo={subscription}
                isLoading={isLoadingSubscription}
              />
            ) : activeTab === 'api-key' ? (
              <ApiKeySettings 
                apiKey={apiKey}
                isLoading={isLoadingApiKey}
                onGenerateApiKey={handleGenerateApiKey}
                onRevokeApiKey={handleRevokeApiKey}
              />
            ) : activeTab === 'mcp' ? (
              <MCPSettings 
                apiKey={apiKey}
                onGenerateApiKey={handleGenerateApiKey}
              />
            ) : activeTab === 'playground' ? (
              <PlaygroundSettings 
                playgroundSettings={playgroundSettings}
                isLoading={isLoadingPlaygroundSettings || isLoadingAvailableModels}
                availableModels={availableModels}
                onSave={handleSavePlaygroundSettings}
                onApiKeySettingsChange={handleApiKeySettingsChange}
              />
            ) : (
              <PlaygroundSettings 
                playgroundSettings={playgroundSettings}
                isLoading={isLoadingPlaygroundSettings || isLoadingAvailableModels}
                availableModels={availableModels}
                onSave={handleSavePlaygroundSettings}
                onApiKeySettingsChange={handleApiKeySettingsChange}
              />
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}