'use client';

import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { UserCircle2, Key, Terminal, CreditCard } from "lucide-react"
import Link from "next/link"
import AccountSettings from "../components/account-settings"
import ApiKeySettings from "../components/api-key-settings"
import MCPSettings from "../components/mcp-settings"
import BillingSettings from "../components/billing-settings"
import { useState, useEffect } from "react"
import { getUserProfile, getUserApiKey, generateApiKey, revokeApiKey, getUserSubscription } from "../api/api.settings"
import { UserProfile, UserApiKey, UserSubscription } from "../api/types.settings"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"

interface AccountSettingsDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  initialTab?: 'account' | 'api-key' | 'mcp' | 'billing'
}

export function AccountSettingsDialog({ 
  open, 
  onOpenChange, 
  initialTab = 'account' 
}: AccountSettingsDialogProps) {
  const [activeTab, setActiveTab] = useState<'account' | 'api-key' | 'mcp' | 'billing'>(initialTab);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [apiKey, setApiKey] = useState<UserApiKey | null>(null);
  const [subscription, setSubscription] = useState<UserSubscription | null>(null);
  const [isLoadingProfile, setIsLoadingProfile] = useState(true);
  const [isLoadingApiKey, setIsLoadingApiKey] = useState(true);
  const [isLoadingSubscription, setIsLoadingSubscription] = useState(true);

  useEffect(() => {
    if (open) {
      const fetchProfile = async () => {
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
      
      fetchProfile();
    }
  }, [open]);

  useEffect(() => {
    if (open && (activeTab === 'api-key' || activeTab === 'mcp')) {
      const fetchApiKey = async () => {
        setIsLoadingApiKey(true);
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
  }, [open, activeTab]);

  useEffect(() => {
    if (open && (activeTab === 'billing')) {
      const fetchSubscription = async () => {
        setIsLoadingSubscription(true);
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
  }, [open, activeTab]);

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
            
            <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as any)}>
              <TabsList className="grid grid-cols-4 w-full">
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
            ) : (
              <MCPSettings 
                apiKey={apiKey}
                onGenerateApiKey={handleGenerateApiKey}
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
                  setActiveTab('account');
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
                  setActiveTab('billing');
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
                  setActiveTab('api-key');
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
                  setActiveTab('mcp');
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
            ) : (
              <MCPSettings 
                apiKey={apiKey}
                onGenerateApiKey={handleGenerateApiKey}
              />
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}