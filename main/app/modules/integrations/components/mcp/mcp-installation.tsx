import { useState } from "react";
import { ArrowUpRight, Loader2, AlertCircle, RefreshCw, Plus, ExternalLink, LogIn } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import Link from "next/link";
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
  onLogin?: () => void;
  isPublic?: boolean;
}

export function McpInstallation({ 
  imageName, 
  mcpDetails, 
  userEnvironment, 
  isConnected = false,
  onConnectionUpdate,
  apiKey,
  onApiKeyGenerated,
  onLogin,
  isPublic = false
}: McpInstallationProps) {
  const [showManageDialog, setShowManageDialog] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  
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
  
  const renderActionButton = () => {
    if (isPublic) {
      return null;
    }
    
    // Get user authentication state
    const hasUser = !isPublic && apiKey;
    
    if (!hasUser) {
      return (
        <Button 
          onClick={onLogin}
          className="gap-2"
        >
          Login
          <LogIn className="h-4 w-4" />
        </Button>
      );
    }
    
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
          onClick={handleConnect}
        >
          Reconnect
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
                <p className="text-muted-foreground mt-1">
                  {isPublic 
                    ? "Login to connect this MCP to your account" 
                    : apiKey 
                      ? "Connect to use this MCP in your applications" 
                      : "Login to connect this MCP to your account"}
                </p>
              </div>
              
              {!isPublic && apiKey && (connectionStatus === "connecting" || connectionStatus === "failed") && (
                <div className="flex items-center gap-2">
                  <span className="text-sm text-muted-foreground">Status:</span>
                  {renderConnectionStatus()}
                </div>
              )}
            </div>
            
            <div className="flex gap-2">
              {!isPublic && apiKey && (
                <Link 
                  href="https://docs.veyrax.com/deployment/connect" 
                  target="_blank" 
                  rel="noopener noreferrer"
                >
                  <Button 
                    variant="link" 
                    className="gap-1"
                  >
                    Docs
                  </Button>
                </Link>
              )}
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
        onLogin={onLogin}
        isPublic={isPublic}
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