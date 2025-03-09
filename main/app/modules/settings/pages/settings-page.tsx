'use client';

import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { UserCircle2, Key, Terminal } from "lucide-react"
import Link from "next/link"
import AccountSettings from "../components/account-settings"
import ApiKeySettings from "../components/api-key-settings"
import MCPSettings from "../components/mcp-settings"
import { useState, useEffect } from "react"
import { getUserProfile, getUserApiKey, generateApiKey, revokeApiKey } from "../api/api.settings"
import { UserProfile, UserApiKey } from "../api/types.settings"

interface AccountSettingsDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  initialTab?: 'account' | 'api-key' | 'mcp'
}

export function AccountSettingsDialog({ 
  open, 
  onOpenChange, 
  initialTab = 'account' 
}: AccountSettingsDialogProps) {
  const [activeTab, setActiveTab] = useState<'account' | 'api-key' | 'mcp'>(initialTab);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [apiKey, setApiKey] = useState<UserApiKey | null>(null);
  const [isLoadingProfile, setIsLoadingProfile] = useState(true);
  const [isLoadingApiKey, setIsLoadingApiKey] = useState(true);

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
        <div className="flex h-full">
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
                <span>MCP</span>
              </Link>
            </nav>
          </div>

          <div className="flex-1 p-6 overflow-y-auto max-h-[80vh]">
            {activeTab === 'account' ? (
              <AccountSettings 
                profile={profile} 
                isLoading={isLoadingProfile} 
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