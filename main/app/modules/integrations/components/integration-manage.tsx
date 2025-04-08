'use client';

import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ManageDialogProps } from "../api/types.integrations";
import { 
  disconnectProvider,
  getUserApiKey,
  enableApiKeyProvider,
  enableDbAccessProvider,
  getUserDbCredentials,
  testDbConnection,
  validateApiKey,
  enableApiKeyWithBaseProvider,
  getProviderBaseUrl,
  getProviderCustomAuth,
  updateProviderCustomAuth,
  validateCustomAuthSchema,
  authenticateWhatsApp,
  checkWhatsAppStatus,
  disconnectWhatsAppProvider,
  enableProvider,
  rentApiKey,
  checkUserHasRentedKey
} from "../api/api.integrations";
import { canUserRentKey } from "@/app/modules/settings/api/api.settings";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { HelpCircle, RefreshCw, AlertCircle, Loader2, QrCode, Key } from "lucide-react";
import { useState, useEffect } from "react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { SnowflakeConfigForm } from "./provider-connection-forms/snowflake-config";
import { VeyraxConfig } from "./provider-connection-forms/veyrax-config";
import { CustomAuthForm } from "./provider-connection-forms/custom-auth-form";
import { EmailAuthForm } from "./provider-connection-forms/email-auth-form";
import { WhatsAppConfigForm } from "./provider-connection-forms/whatsapp-config";

interface WhatsAppConfig {
  phone?: string;
  isLoggedIn: boolean;
}

export function ManageDialog({ provider, open, onClose, onUpdate, encrypted_api_key, code }: ManageDialogProps & { encrypted_api_key?: string, code?: string }) {
  const [apiKey, setApiKey] = useState<string>("");
  const [originalApiKey, setOriginalApiKey] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [hasRentedKey, setHasRentedKey] = useState<boolean>(false);
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
  const [customAuthData, setCustomAuthData] = useState<Record<string, any>>({});
  const [originalCustomAuthData, setOriginalCustomAuthData] = useState<Record<string, any>>({});
  const [connectionError, setConnectionError] = useState<string | null>(null);
  const [shouldCloseAfterUpdate, setShouldCloseAfterUpdate] = useState(true);
  const [apiKeyChanged, setApiKeyChanged] = useState(false);
  const [customAuthChanged, setCustomAuthChanged] = useState(false);
  const [isValidating, setIsValidating] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);
  const [baseUrl, setBaseUrl] = useState<string>("");
  const [originalBaseUrl, setOriginalBaseUrl] = useState<string>("");
  const [whatsappConfig, setWhatsappConfig] = useState<WhatsAppConfig>({
    isLoggedIn: false,
    phone: undefined
  });
  const [canRentKeys, setCanRentKeys] = useState<boolean>(false);

  useEffect(() => {
    if (open) {
      if (provider.auth_method === 'api_key' || provider.auth_method === 'api_key_with_base') {
        fetchApiKey();
        setApiKeyChanged(false);
        checkRentedKey();
        
        if (provider.auth_method === 'api_key_with_base') {
          fetchBaseUrl();
        }
      } else if (provider.auth_method === 'db_access') {
        fetchDbCredentials();
      } else if (provider.auth_method === 'custom') {
        fetchCustomAuth();
        setCustomAuthChanged(false);
      } else if (provider.provider_tag === 'whatsapp') {
        checkWhatsAppConnectionStatus();
      }
    }
    if (open && provider.is_rentable) {
      checkRentPermission();
    }
  }, [open, provider.id, provider.auth_method, provider.provider_tag, provider.connected, provider.is_rentable]);

  const fetchApiKey = async () => {
    if (provider.auth_method !== 'api_key' && provider.auth_method !== 'api_key_with_base') return;
    
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

  const fetchBaseUrl = async () => {
    if (provider.auth_method !== 'api_key_with_base') return;
    
    setIsLoading(true);
    try {
      const url = await getProviderBaseUrl(provider.id);
      setBaseUrl(url || "");
      setOriginalBaseUrl(url || "");
    } catch (error) {
      console.error('Failed to fetch base URL:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchCustomAuth = async () => {
    if (provider.auth_method !== 'custom') return;
    
    setIsLoading(true);
    try {
      const authData = await getProviderCustomAuth(provider.id);
      if (authData) {
        setCustomAuthData(authData);
        setOriginalCustomAuthData(JSON.parse(JSON.stringify(authData)));
      } else {
        setCustomAuthData({});
        setOriginalCustomAuthData({});
      }
    } catch (error) {
      console.error('Failed to fetch custom auth data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const checkWhatsAppConnectionStatus = async () => {
    setIsLoading(true);
    setValidationError(null);
    
    try {
      // First try to get data from custom auth
      const customAuthData = await getProviderCustomAuth(provider.id);
      
      // Handle various formats of is_logged_in which might be stored in the DB
      const isLoggedIn = 
        customAuthData?.is_logged_in === true || 
        customAuthData?.is_logged_in === 'true' || 
        customAuthData?.isLoggedIn === true || 
        customAuthData?.isLoggedIn === 'true';
      
      if (customAuthData && isLoggedIn) {
        setWhatsappConfig({
          isLoggedIn: true,
          phone: customAuthData.phone || customAuthData.phoneNumber
        });
        
        // Update provider connection status if it's now connected
        if (!provider.connected) {
          onUpdate();
        }
        
        setIsLoading(false);
        return;
      }
      
      // If no custom auth data or not logged in, check status from API
      const result = await checkWhatsAppStatus(encrypted_api_key, code);
      
      if (result.success) {
        setWhatsappConfig({
          isLoggedIn: result.isLoggedIn,
          phone: result.phone
        });
        
        if (result.isLoggedIn) {
          // Update provider connection status if it's now connected
          if (!provider.connected) {
            onUpdate();
          }
        }
      } else {
        console.warn("WhatsApp status check returned error:", result.message);
        // Don't show error to user as this is just an initial check
      }
    } catch (error) {
      console.error("Error checking WhatsApp status:", error);
      // Don't show error to user as this is just an initial check
    } finally {
      setIsLoading(false);
    }
  };

  const checkRentPermission = async () => {
    try {
      const { allowed } = await canUserRentKey();
      setCanRentKeys(allowed);
    } catch (error) {
      console.error('Failed to check rent permission:', error);
      setCanRentKeys(false);
    }
  };

  const checkRentedKey = async () => {
    if (!provider.is_rentable) return;
    try {
      const hasKey = await checkUserHasRentedKey(provider.id);
      setHasRentedKey(hasKey);
    } catch (error) {
      console.error('Failed to check rented key:', error);
    }
  };

  const handleSaveApiKey = async () => {
    if (provider.auth_method === 'api_key') {
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

        await enableApiKeyProvider(provider.id, apiKey, encrypted_api_key, code); 
        onUpdate();
        onClose();
      } catch (error) {
        console.error("Error saving API key:", error);
        setValidationError(error instanceof Error ? error.message : "Failed to save API key");
      } finally {
        setIsValidating(false);
      }
    } else if (provider.auth_method === 'api_key_with_base') {
      if (apiKey === originalApiKey && baseUrl === originalBaseUrl) {
        onClose();
        return;
      }

      if (!apiKey.trim()) {
        setValidationError("API key is required");
        return;
      }

      if (!baseUrl.trim()) {
        setValidationError("Base URL is required");
        return;
      }

      setIsValidating(true);
      setValidationError(null);

      try {
        const validationResult = await validateApiKey(provider.provider_tag, apiKey, baseUrl);
        
        if (!validationResult.valid) {
          setValidationError(validationResult.message);
          setIsValidating(false);
          return;
        }

        await enableApiKeyWithBaseProvider(provider.id, apiKey, baseUrl, encrypted_api_key, code);
        onUpdate();
        onClose();
      } catch (error) {
        console.error("Error saving API key with base URL:", error);
        setValidationError(error instanceof Error ? error.message : "Failed to save configuration");
      } finally {
        setIsValidating(false);
      }
    }
  };

  const handleSaveDbConfig = async () => {
    setIsSaving(true);
    setConnectionError(null);
    
    try {
      const testResult = await testDbConnection(provider.id, dbConfig, encrypted_api_key, code);
      
      if (!testResult.success) {
        setConnectionError(testResult.message || "Connection test failed");
        setIsSaving(false);
        return;
      }
      
      await enableDbAccessProvider(provider.id, dbConfig, encrypted_api_key, code);
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

  const handleSaveCustomAuth = async () => {
    if (!customAuthChanged) {
      onClose();
      return;
    }

    // Validate required fields
    if (provider.auth_schema) {
      const requiredFields = provider.auth_schema.filter(field => field.required);
      for (const field of requiredFields) {
        if (!customAuthData[field.key] && customAuthData[field.key] !== false) {
          setValidationError(`${field.label} is required`);
          return;
        }
      }
    }

    setIsValidating(true);
    setValidationError(null);

    try {
      // Extract only the changed fields to send to the API
      const changedFields: Record<string, any> = {};
      
      // Compare current data with original data
      Object.keys(customAuthData).forEach(key => {
        // If the field is new or has changed, include it
        if (
          !originalCustomAuthData.hasOwnProperty(key) || 
          JSON.stringify(customAuthData[key]) !== JSON.stringify(originalCustomAuthData[key])
        ) {
          changedFields[key] = customAuthData[key];
        }
      });
      
      // If there are no changes, just close the dialog
      if (Object.keys(changedFields).length === 0) {
        onClose();
        return;
      }
      
      const validateSchema = await validateCustomAuthSchema(provider.id, customAuthData);
      if (!validateSchema.valid) {
        setValidationError(validateSchema.message);
        setIsValidating(false);
        return;
      }
      
      // TODO: validation is tricky cause some fields are encrypted.
      // const validationResult = await validateCustomAuth(provider.id, changedFields);
      

      // Only send the changed fields to the API
      await updateProviderCustomAuth(provider.id, changedFields, encrypted_api_key, code);
      onUpdate();
      onClose();
    } catch (error) {
      console.error("Error saving custom auth data:", error);
      setValidationError(error instanceof Error ? error.message : "Failed to save authentication data");
    } finally {
      setIsValidating(false);
    }
  };

  const handleDisconnect = async () => {
    if (isLoading) return;
    
    setIsLoading(true);
    try {
      if (provider.provider_tag === 'whatsapp') {
        await disconnectWhatsAppProvider(provider.id, encrypted_api_key, code);
      } else {
        await disconnectProvider(provider.id, encrypted_api_key, code );
      }
      onUpdate();
      onClose();
    } catch (error) {
      console.error('Failed to disconnect provider:', error);
      setValidationError(error instanceof Error ? error.message : 'Failed to disconnect provider');
    } finally {
      setIsLoading(false);
    }
  };

  const handleVeyraxUpdate = () => {
    if (onUpdate) onUpdate();
  };

  const handleConnectSimpleProvider = async () => {
    setIsLoading(true);
    try {
      await enableProvider(provider.id, encrypted_api_key, code);
      if (onUpdate) {
        onUpdate();
      }
      onClose();
    } catch (error) {
      console.error(`Failed to connect ${provider.name}:`, error);
      setValidationError(error instanceof Error ? error.message : "Failed to connect to service");
    } finally {
      setIsLoading(false);
    }
  };

  const handleRentKey = async () => {
    if (isLoading) return;
    
    setIsLoading(true);
    setValidationError(null);
    
    try {
      await rentApiKey(provider.id, encrypted_api_key, code);
      onUpdate();
      onClose();
    } catch (error) {
      console.error('Error renting API key:', error);
      setValidationError(error instanceof Error ? error.message : 'Failed to rent API key');
    } finally {
      setIsLoading(false);
    }
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

  const renderCustomAuthForm = () => {
    if (!provider.auth_schema || provider.auth_schema.length === 0) {
      return (
        <div className="p-4 border rounded bg-amber-50 text-amber-800">
          No authentication schema defined for this provider.
        </div>
      );
    }

    const isMail = provider.provider_tag === 'mail' || provider.name?.toLowerCase().includes('gmail') || provider.name?.toLowerCase().includes('smtp');
    
    return (
      <>
        {isMail && (
          <div className="p-3 border rounded-lg bg-amber-50 border-amber-200 -mt-2 mb-3">
            <p className="text-sm text-amber-700">
              To connect your email, enter your Gmail address and an app password.
              {provider.name?.toLowerCase().includes('gmail') && (
                <> You can generate an app password at <a href="https://myaccount.google.com/apppasswords" target="_blank" rel="noopener noreferrer" className="text-amber-900 underline">myaccount.google.com/apppasswords</a>.</>
              )}
            </p>
          </div>
        )}
        <CustomAuthForm
          authSchema={provider.auth_schema}
          authData={customAuthData}
          onChange={(authData) => {
            setCustomAuthData(authData);
            setCustomAuthChanged(true);
            setValidationError(null);
          }}
          disabled={isValidating || isLoading}
        />
      </>
    );
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
          {provider.auth_method === 'none' && (
            <>
              {validationError && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
                  <span className="block sm:inline">{validationError}</span>
                </div>
              )}
            </>
          )}

          {provider.auth_method === 'oauth' && provider.user_scopes && (
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
                {provider.user_scopes.map((scope) => (
                  <Badge 
                    key={`${scope.scope_id}-${scope.scope_name}`} 
                    variant="secondary" 
                    className="bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300 transition-colors"
                  >
                    {scope.scope_name || scope.scope_id}
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

          {provider.provider_tag === 'whatsapp' && (
            <WhatsAppConfigForm 
              providerId={provider.id}
              config={whatsappConfig}
              onChange={setWhatsappConfig}
              disabled={isLoading}
              onUpdate={onUpdate}
              encrypted_api_key={encrypted_api_key}
              code={code}
            />
          )}

          {(provider.auth_method === 'api_key' || provider.auth_method === 'api_key_with_base') && (
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
                    setApiKeyChanged(e.target.value !== originalApiKey || baseUrl !== originalBaseUrl);
                    setValidationError(null);
                  }}
                  placeholder={hasRentedKey ? "Using Veyrax Rented API Key" : "Enter your API key"}
                  className="w-full"
                  disabled={isValidating || hasRentedKey}
                />
              </div>
              
              {provider.auth_method === 'api_key_with_base' && (
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <Label htmlFor="baseUrl" className="text-sm font-medium">Base URL</Label>
                  </div>
                  <Input
                    id="baseUrl"
                    type="text"
                    value={baseUrl}
                    onChange={(e) => {
                      setBaseUrl(e.target.value);
                      setApiKeyChanged(apiKey !== originalApiKey || e.target.value !== originalBaseUrl);
                      setValidationError(null);
                    }}
                    placeholder="Enter the base URL (e.g., https://example.com/api)"
                    className="w-full"
                    disabled={isValidating || hasRentedKey}
                  />
                </div>
              )}
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

          {provider.auth_method === 'custom' && (
            <div className="space-y-4">
              {validationError && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
                  <span className="block sm:inline">{validationError}</span>
                </div>
              )}
              
              <div className="space-y-2">
                {renderCustomAuthForm()}
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
            provider.auth_method === 'api_key_with_base' ||
            provider.auth_method === 'custom' ||
            provider.provider_tag === 'whatsapp' ||
            (provider.provider_tag && provider.provider_tag.toLowerCase() === 'veyrax')
          ) && (
            <div className="flex gap-2">
              <Button
                variant="destructive"
                onClick={handleDisconnect}
                disabled={isLoading}
              >
                {isLoading ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                  </>
                ) : (
                  'Disconnect'
                )}
              </Button>
            </div>
          )}
          
          {provider.is_rentable && canRentKeys && !provider.connected && (
            <Button
              variant="outline"
              className="gap-2"
              onClick={handleRentKey}
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                </>
              ) : (
                <>
                  <Key className="h-4 w-4" />
                  Rent Key
                </>
              )}
            </Button>
          )}
          
          {provider.auth_method === 'none' && !provider.connected && (
            <Button 
              onClick={handleConnectSimpleProvider} 
              disabled={isLoading}
            >
              {isLoading ? (
                <RefreshCw className="h-4 w-4 animate-spin" />
              ) : (
                "Connect"
              )}
            </Button>
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
          
          {(provider.auth_method === 'api_key' || provider.auth_method === 'api_key_with_base') && (
            <Button 
              onClick={handleSaveApiKey} 
              disabled={
                (provider.auth_method === 'api_key' && (!apiKey.trim() || isValidating || !apiKeyChanged)) ||
                (provider.auth_method === 'api_key_with_base' && (!apiKey.trim() || !baseUrl.trim() || isValidating || !apiKeyChanged))
              }
            >
              {isValidating ? (
                <>
                  <RefreshCw className="h-4 w-4 animate-spin" />
                </>
              ) : (
                "Save Configuration"
              )}
            </Button>
          )}

          {provider.auth_method === 'custom' && (
            <Button 
              onClick={handleSaveCustomAuth} 
              disabled={isLoading || isValidating || !customAuthChanged}
            >
              {isValidating ? (
                <>
                  <RefreshCw className="h-4 w-4 animate-spin" />
                </>
              ) : (
                "Save Configuration"
              )}
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}