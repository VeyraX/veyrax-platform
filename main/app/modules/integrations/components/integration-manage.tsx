'use client';

import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Provider, ManageDialogProps } from "../api/types.integrations";
import { disconnectProvider, getUserApiKey, enableApiKeyProvider, enableDbAccessProvider, getUserDbCredentials, testDbConnection, validateApiKey } from "../api/api.integrations";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { HelpCircle, RefreshCw, AlertCircle, Loader2 } from "lucide-react";
import { useState, useEffect } from "react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { SnowflakeConfigForm } from "./provider-connection-forms/snowflake-config";
import { VeyraxConfig } from "./provider-connection-forms/veyrax-config";

export function ManageDialog({ provider, open, onClose, onUpdate }: ManageDialogProps) {
  const [apiKey, setApiKey] = useState<string>("");
  const [originalApiKey, setOriginalApiKey] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [dbConfig, setDbConfig] = useState({
    host: "",
    port: "5432",
    dbname: "",
    user: "",
    password: "",
    schema: "public",
    account: "",
    warehouse: "",
    database: "",
    role: ""
  });
  const [connectionError, setConnectionError] = useState<string | null>(null);
  const [shouldCloseAfterUpdate, setShouldCloseAfterUpdate] = useState(true);
  const [apiKeyChanged, setApiKeyChanged] = useState(false);
  const [isValidating, setIsValidating] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);

  useEffect(() => {
    if (open) {
      if (provider.auth_method === 'api_key') {
        fetchApiKey();
        setApiKeyChanged(false);
      } else if (provider.auth_method === 'db_access') {
        fetchDbCredentials();
      }
    }
  }, [open, provider.id, provider.auth_method]);

  const fetchApiKey = async () => {
    if (provider.auth_method !== 'api_key') return;
    
    setIsLoading(true);
    try {
      const key = await getUserApiKey(provider.id);
      setApiKey(key || "");
      setOriginalApiKey(key || "");
    } catch (error) {
      console.error('Failed to fetch API key:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchDbCredentials = async () => {
    if (provider.auth_method !== 'db_access') return;
    
    setIsLoading(true);
    try {
      const credentials = await getUserDbCredentials(provider.id);
      if (credentials) {
        if (provider.provider_tag === 'snowflake') {
          setDbConfig({
            ...dbConfig,
            account: credentials.account || "",
            user: credentials.user || "",
            password: credentials.password || "",
            warehouse: credentials.warehouse || "",
            database: credentials.database || "",
            schema: credentials.schema || "PUBLIC",
            role: credentials.role || ""
          });
        } else {
          setDbConfig({
            ...dbConfig,
            host: credentials.host || "",
            port: credentials.port || "5432",
            dbname: credentials.dbname || "",
            user: credentials.user || "",
            password: credentials.password || "",
            schema: credentials.schema || "public"
          });
        }
      }
    } catch (error) {
      console.error('Failed to fetch database credentials:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSaveApiKey = async () => {
    if (apiKey === originalApiKey) {
      onClose();
      return;
    }

    if (!apiKey.trim()) {
      setValidationError("API key is required");
      return;
    }

    setIsValidating(true);
    setValidationError(null);

    try {
      const validationResult = await validateApiKey(provider.provider_tag, apiKey);
      
      if (!validationResult.valid) {
        setValidationError(validationResult.message);
        setIsValidating(false);
        return;
      }

      await enableApiKeyProvider(provider.id, apiKey);
      onUpdate();
      onClose();
    } catch (error) {
      console.error("Error saving API key:", error);
      setValidationError(error instanceof Error ? error.message : "Failed to save API key");
    } finally {
      setIsValidating(false);
    }
  };

  const handleSaveDbConfig = async () => {
    setIsSaving(true);
    setConnectionError(null);
    
    try {
      const testResult = await testDbConnection(provider.id, dbConfig);
      
      if (!testResult.success) {
        setConnectionError(testResult.message || "Connection test failed");
        setIsSaving(false);
        return;
      }
      
      await enableDbAccessProvider(provider.id, dbConfig);
      setConnectionError(null);
      onUpdate();
      onClose();
    } catch (error) {
      console.error('Failed to save database configuration:', error);
      setConnectionError(error instanceof Error ? error.message : 'An unexpected error occurred');
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

  const handleVeyraxUpdate = () => {
    if (onUpdate) onUpdate();
  };

  const renderDbConfigForm = () => {
    if (provider.provider_tag === 'snowflake') {
      return (
        <SnowflakeConfigForm 
          config={dbConfig} 
          onChange={setDbConfig} 
          disabled={isLoading}
        />
      );
    } else {
      return (
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="host">Host</Label>
            <Input
              id="host"
              value={dbConfig.host}
              onChange={(e) => setDbConfig({...dbConfig, host: e.target.value})}
              placeholder="e.g., db.example.com"
              disabled={isLoading}
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="port">Port</Label>
            <Input
              id="port"
              value={dbConfig.port}
              onChange={(e) => setDbConfig({...dbConfig, port: e.target.value})}
              placeholder="e.g., 5432"
              disabled={isLoading}
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="dbname">Database Name</Label>
            <Input
              id="dbname"
              value={dbConfig.dbname}
              onChange={(e) => setDbConfig({...dbConfig, dbname: e.target.value})}
              placeholder="e.g., postgres"
              disabled={isLoading}
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="user">Username</Label>
            <Input
              id="user"
              value={dbConfig.user}
              onChange={(e) => setDbConfig({...dbConfig, user: e.target.value})}
              placeholder="e.g., postgres"
              disabled={isLoading}
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="password">Password</Label>
            <Input
              id="password"
              type="password"
              value={dbConfig.password}
              onChange={(e) => setDbConfig({...dbConfig, password: e.target.value})}
              placeholder={provider.connected ? "••••••" : "Enter password"}
              disabled={isLoading}
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="schema">Schema</Label>
            <Input
              id="schema"
              value={dbConfig.schema}
              onChange={(e) => setDbConfig({...dbConfig, schema: e.target.value})}
              placeholder="e.g., public"
              disabled={isLoading}
            />
          </div>
        </div>
      );
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[600px] max-h-[80vh] overflow-y-auto">
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
                  <Badge key={scope.scope} variant="secondary" className="bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300 transition-colors">
                    {scope.scope_name}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {provider.provider_tag && provider.provider_tag.toLowerCase() === 'veyrax' && (
            <VeyraxConfig 
              onUpdate={handleVeyraxUpdate}
              disabled={isLoading}
            />
          )}

          {provider.auth_method === 'api_key' && (
            <div className="space-y-4">
              {validationError && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
                  <span className="block sm:inline">{validationError}</span>
                </div>
              )}
              
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Label htmlFor="apiKey" className="text-sm font-medium">API Key</Label>
                </div>
                <Input
                  id="apiKey"
                  type="password"
                  value={apiKey}
                  onChange={(e) => {
                    setApiKey(e.target.value);
                    setApiKeyChanged(e.target.value !== originalApiKey);
                    setValidationError(null);
                  }}
                  placeholder="Enter your API key"
                  className="w-full"
                  disabled={isValidating}
                />
              </div>
            </div>
          )}

          {provider.auth_method === 'db_access' && (
            <div className="space-y-4">
              {connectionError && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
                  <span className="block sm:inline">{connectionError}</span>
                </div>
              )}
              
              <div className="space-y-2">
                {renderDbConfigForm()}
              </div>
            </div>
          )}
        </div>

        <DialogFooter className="flex justify-between">
          {provider.connected && (
            provider.auth_method === 'oauth' || 
            provider.auth_method === 'db_access' || 
            provider.auth_method === 'none' || 
            provider.auth_method === 'api_key' ||
            (provider.provider_tag && provider.provider_tag.toLowerCase() === 'veyrax')
          ) && (
            <div className="flex gap-2">
              <Button
                variant="destructive"
                onClick={handleDisconnect}
              >
                Disconnect
              </Button>
            </div>
          )}
          
          {provider.auth_method === 'db_access' && !provider.connected && (
            <Button 
              onClick={handleSaveDbConfig} 
              disabled={isLoading || isSaving}
            >
              {isSaving ? (
                <RefreshCw className="h-4 w-4 animate-spin" />
              ) : (
                "Save Connection"
              )}
            </Button>
          )}
          
          {provider.auth_method === 'api_key' && (
            <Button 
              onClick={handleSaveApiKey} 
              disabled={!apiKey.trim() || isValidating || !apiKeyChanged}
            >
              {isValidating ? (
                <>
                  <RefreshCw className="h-4 w-4 animate-spin" />
                </>
              ) : (
                "Save API Key"
              )}
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}