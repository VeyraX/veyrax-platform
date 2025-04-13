'use client';

import { useState, useEffect } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { AlertCircle, Loader2, RefreshCw } from "lucide-react";
import { createClient } from "@/lib/utils/supabase/client";
import { saveUserMcpEnvironment, disconnectUserMcp } from "@/app/modules/integrations/api/api.integrations.mcp";

interface McpManageProps {
  imageName: string;
  open: boolean;
  onClose: (connected?: boolean) => void;
  predefinedEnv?: Record<string, any>;
  repositoryId?: string;
  isConnected?: boolean;
  onConnectionUpdate?: () => Promise<void>;
}

interface EnvVar {
  key: string;
  value: string;
}

export function McpManage({ 
  imageName, 
  open, 
  onClose, 
  predefinedEnv = {}, 
  repositoryId,
  isConnected = false,
  onConnectionUpdate
}: McpManageProps) {
  const [envVars, setEnvVars] = useState<EnvVar[]>([]);
  const [originalEnvVars, setOriginalEnvVars] = useState<EnvVar[]>([]);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [envChanged, setEnvChanged] = useState<boolean>(false);
  const supabase = createClient();

  useEffect(() => {
    if (open) {
      const envVarsArray = Object.entries(predefinedEnv).map(([key, value]) => ({
        key,
        value: typeof value === 'string' ? value : String(value) 
      }));
      
      setEnvVars(envVarsArray);
      setOriginalEnvVars(JSON.parse(JSON.stringify(envVarsArray)));
      setErrorMessage(null);
      setEnvChanged(false);
    }
  }, [open, predefinedEnv]);

  const handleEnvVarChange = (index: number, value: string) => {
    const newVars = [...envVars];
    newVars[index].value = value;
    setEnvVars(newVars);
    
    const hasChanges = newVars.some((envVar, idx) => {
      return envVar.value !== originalEnvVars[idx]?.value;
    });
    
    setEnvChanged(hasChanges);
  };

  const handleSave = async () => {
    if (!envChanged) {
      onClose();
      return;
    }
    
    setIsSaving(true);
    setErrorMessage(null);
    
    try {
      const envObject: Record<string, string> = {};
      envVars.forEach(v => {
        envObject[v.key] = v.value;
      });
      
      if (repositoryId) {
        // Save to users_mcp table using the new function
        const success = await saveUserMcpEnvironment(repositoryId, envObject);
        
        if (!success) {
          throw new Error("Failed to save configuration");
        }
      } else {
        // Fallback to the previous method if repositoryId is not provided
        const { error } = await supabase
          .from('user_mcp_connections')
          .upsert({ 
            image_name: imageName,
            env_vars: envObject,
            connected: true
          });
          
        if (error) {
          throw error;
        }
      }
      
      if (onConnectionUpdate) {
        await onConnectionUpdate();
      }
      
      onClose(true);
    } catch (error) {
      console.error("Error saving environment variables:", error);
      setErrorMessage("Failed to save configuration");
    } finally {
      setIsSaving(false);
    }
  };

  const handleDisconnect = async () => {
    if (isLoading || !repositoryId) return;
    
    setIsLoading(true);
    setErrorMessage(null);
    
    try {
      const success = await disconnectUserMcp(repositoryId);
      
      if (!success) {
        throw new Error("Failed to disconnect MCP");
      }
      
      if (onConnectionUpdate) {
        await onConnectionUpdate();
      }
      
      onClose(false);
    } catch (error) {
      console.error("Error disconnecting MCP:", error);
      setErrorMessage("Failed to disconnect MCP");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={() => onClose()}>
      <DialogContent className="sm:max-w-[600px] max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            {imageName} Settings
          </DialogTitle>
        </DialogHeader>

        <div className="flex flex-col gap-6 py-4">
          {errorMessage && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
              <span className="block sm:inline">{errorMessage}</span>
            </div>
          )}
          
          {envVars.length > 0 ? (
            <div className="space-y-4">
              {envVars.map((envVar, index) => (
                <div key={index} className="space-y-2">
                  <div className="flex items-center gap-2">
                    <Label htmlFor={`envVar-${index}`} className="text-sm font-medium">{envVar.key}</Label>
                  </div>
                  <Input
                    id={`envVar-${index}`}
                    type="text"
                    value={envVar.value} 
                    onChange={(e) => handleEnvVarChange(index, e.target.value)}
                    placeholder={`Enter ${envVar.key}`}
                    className="w-full"
                    disabled={isSaving || isLoading}
                  />
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-4 text-muted-foreground">
              No environment variables defined for this MCP
            </div>
          )}
        </div>

        <DialogFooter className="flex justify-between">
          {isConnected && (
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
          
          <Button 
            onClick={handleSave} 
            disabled={isSaving || isLoading || !envChanged}
          >
            {isSaving ? (
              <>
                <RefreshCw className="h-4 w-4 animate-spin" />
              </>
            ) : (
              'Save Configuration'
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
} 