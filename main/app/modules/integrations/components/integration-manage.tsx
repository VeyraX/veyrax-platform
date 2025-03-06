'use client';

import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Provider, ManageDialogProps } from "../api/types.integrations";
import { disconnectProvider, getUserApiKey, enableApiKeyProvider } from "../api/api.integrations";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { HelpCircle, RefreshCw } from "lucide-react";
import { useState, useEffect } from "react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export function ManageDialog({ provider, open, onClose, onUpdate }: ManageDialogProps) {
  const [apiKey, setApiKey] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isSaving, setIsSaving] = useState<boolean>(false);

  useEffect(() => {
    if (open && provider.auth_method === 'api_key') {
      fetchApiKey();
    }
  }, [open, provider.id]);

  const fetchApiKey = async () => {
    if (provider.auth_method !== 'api_key') return;
    
    setIsLoading(true);
    try {
      const key = await getUserApiKey(provider.id);
      setApiKey(key || "");
    } catch (error) {
      console.error('Failed to fetch API key:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSaveApiKey = async () => {
    setIsSaving(true);
    try {
      await enableApiKeyProvider(provider.id, apiKey.trim());
      onUpdate();
      onClose();
    } catch (error) {
      console.error('Failed to save API key:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const handleDisconnect = async () => {
    try {
      await disconnectProvider(provider.id);
      onUpdate();
      onClose();
    } catch (error) {
      console.error('Failed to disconnect provider:', error);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <img
              src={provider.logo_url || '/default-logo.svg'}
              alt={provider.name}
              className="w-6 h-6 rounded"
            />
            {provider.name} Settings
          </DialogTitle>
        </DialogHeader>

        <div className="flex flex-col gap-6 py-4">
          {/* OAuth Scopes */}
          {provider.auth_method === 'oauth' && provider.scopes && (
            <div className="grid grid-cols-2 gap-4">
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-medium">Authorized Scopes</h3>
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <HelpCircle className="h-4 w-4 text-muted-foreground" />
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>To change scopes, please disconnect and reconnect with new permissions</p>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
              </div>
              <div className="flex flex-wrap gap-2 justify-end">
                {provider.scopes.map((scope) => (
                  <Badge key={scope.scope} variant="secondary" className="bg-gray-900/20 text-gray-400 dark:bg-gray-900/30 dark:text-gray-300 transition-colors">
                    {scope.scope_name}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {/* API Key Input */}
          {provider.auth_method === 'api_key' && (
            <div className="space-y-4">
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Label htmlFor="apiKey" className="text-sm font-medium">API Key</Label>
                </div>
                <div className="flex gap-2">
                  <div className="relative flex-1">
                    <Input
                      id="apiKey"
                      type="password"
                      value={apiKey}
                      onChange={(e) => setApiKey(e.target.value)}
                      placeholder={apiKey ? "••••••••••••••••••••••" : "Enter your API key"}
                      className="pr-10"
                      disabled={isLoading}
                    />
                  </div>
                  <Button 
                    onClick={handleSaveApiKey} 
                    disabled={isLoading || isSaving}
                  >
                    {isSaving ? (
                      <RefreshCw className="h-4 w-4 animate-spin" />
                    ) : (
                      "Save"
                    )}
                  </Button>
                </div>
              </div>
            </div>
          )}
        </div>

        <DialogFooter className="flex justify-between">
          {provider.auth_method === 'oauth' && (
            <div className="flex gap-2">
              <Button
                variant="destructive"
                onClick={handleDisconnect}
              >
                Disconnect
              </Button>
            </div>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}