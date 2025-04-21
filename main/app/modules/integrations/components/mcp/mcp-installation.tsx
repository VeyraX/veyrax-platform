import { useState } from "react";
import { ArrowUpRight, Loader2, AlertCircle, RefreshCw, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { McpManage } from "./mcp-manage";
import { McpUsage } from "./mcp-usage";
import { McpDetails, UserMcpEnvironment } from "@/app/modules/integrations/api/types.integrations.mcp";

interface McpInstallationProps {
  imageName: string;
  mcpDetails?: McpDetails | null;
  userEnvironment?: UserMcpEnvironment | null;
  isConnected?: boolean;
  onConnectionUpdate?: () => Promise<void>;
  apiKey?: string;
  onApiKeyGenerated?: (apiKey: string) => void;
}

export function McpInstallation({ 
  imageName, 
  mcpDetails, 
  userEnvironment, 
  isConnected = false,
  onConnectionUpdate,
  apiKey,
  onApiKeyGenerated
}: McpInstallationProps) {
  const [showManageDialog, setShowManageDialog] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  
  // Get information about connection status
  const connectionStatus = userEnvironment?.status || (isConnected ? "connected" : "disconnected");
  const connectionError = userEnvironment?.error || null;
  
  const handleConnect = () => {
    setShowManageDialog(true);
  };
  
  const handleManageClose = async (connected?: boolean) => {
    setShowManageDialog(false);
    
    if (connected && onConnectionUpdate) {
      await onConnectionUpdate();
    }
  };

  const handleRefresh = async () => {
    if (!onConnectionUpdate || isRefreshing) return;
    
    setIsRefreshing(true);
    try {
      await onConnectionUpdate();
    } catch (error) {
      console.error("Failed to refresh connection status:", error);
    } finally {
      setIsRefreshing(false);
    }
  };
  
  // Function to render connection status badge
  const renderConnectionStatus = () => {
    if (connectionStatus === "connecting") {
      return (
        <Badge variant="secondary" className="bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300 transition-colors text-xs flex items-center gap-1">
          <Loader2 className="h-3 w-3 animate-spin" />
          Connecting...
        </Badge>
      );
    }
    
    if (connectionStatus === "failed") {
      return (
        <Badge variant="secondary" className="bg-red-50 text-red-700 dark:bg-red-900/30 dark:text-red-300 transition-colors text-xs flex items-center gap-1">
          <AlertCircle className="h-3 w-3" />
          Failed
        </Badge>
      );
    }
    
    if (connectionStatus === "connected") {
      return (
        <Badge variant="secondary" className="bg-green-50 text-green-700 dark:bg-green-900/30 dark:text-green-300 transition-colors text-xs">
          Connected
        </Badge>
      );
    }
    
    return null;
  };
  
  // Function to render action button based on status
  const renderActionButton = () => {
    if (connectionStatus === "connecting") {
      return (
        <Button 
          variant="outline"
          onClick={handleRefresh}
          disabled={isRefreshing}
          className="gap-2"
        >
          <RefreshCw className={`h-4 w-4 ${isRefreshing ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      );
    }
    
    if (connectionStatus === "failed") {
      return (
        <Button 
          variant="outline"
          size="sm"
          onClick={handleConnect}
          className="text-xs"
        >
          Reconnect
          <Plus className="h-3 w-3 ml-1" />
        </Button>
      );
    }
    
    if (connectionStatus === "connected") {
      return (
        <Button 
          onClick={handleConnect}
          className="gap-2"
          variant="outline"
        >
          Manage
          <ArrowUpRight className="h-4 w-4" />
        </Button>
      );
    }
    
    return (
      <Button 
        onClick={handleConnect}
        className="gap-2"
      >
        Connect
      </Button>
    );
  };
  
  return (
    <>
      <div className="bg-white dark:bg-gray-900 rounded-md border border-gray-200 dark:border-gray-800 mb-6">
        <div className="p-6">
          <div className="flex justify-between items-center">
            <div className="space-y-3">
              <div>
                <h2 className="text-xl font-medium text-foreground">Connection</h2>
                <p className="text-muted-foreground mt-1">Connect to use this MCP in your applications</p>
              </div>
              
              {(connectionStatus === "connecting" || connectionStatus === "failed") && (
                <div className="flex items-center gap-2">
                  <span className="text-sm text-muted-foreground">Status:</span>
                  {renderConnectionStatus()}
                </div>
              )}
            </div>
            
            <div>
              {renderActionButton()}
            </div>
          </div>
        </div>
      </div>
      
      {/* Usage Component */}
      <McpUsage 
        imageName={imageName}
        mcpDetails={mcpDetails}
        userEnvironment={userEnvironment}
        isConnected={isConnected}
        apiKey={apiKey}
        onApiKeyGenerated={onApiKeyGenerated}
      />

      {/* MCP Manage Dialog */}
      {showManageDialog && (
        <McpManage
          imageName={imageName}
          open={showManageDialog}
          onClose={handleManageClose}
          predefinedEnv={userEnvironment?.env || mcpDetails?.env || {}}
          repositoryId={mcpDetails?.id}
          isConnected={isConnected}
          onConnectionUpdate={onConnectionUpdate}
          connectionError={connectionError}
        />
      )}
    </>
  );
} 