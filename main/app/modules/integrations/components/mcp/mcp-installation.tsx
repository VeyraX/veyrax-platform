import { useState } from "react";
import { Code, Check, CopyIcon, CheckIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { McpManage } from "./mcp-manage";
import { McpDetails } from "@/app/modules/integrations/api/types.integrations.mcp";

interface McpUsageProps {
  imageName: string;
  mcpDetails?: McpDetails | null;
}

export function McpUsage({ imageName, mcpDetails }: McpUsageProps) {
  const [isConnected, setIsConnected] = useState(false);
  const [copiedRequest, setCopiedRequest] = useState(false);
  const [copiedResponse, setCopiedResponse] = useState(false);
  const [showManageDialog, setShowManageDialog] = useState(false);
  
  const handleConnect = () => {
    setShowManageDialog(true);
  };
  
  const handleManageClose = (connected: boolean = false) => {
    setShowManageDialog(false);
    
    if (connected) {
      setIsConnected(true);
      setTimeout(() => {
        setIsConnected(false);
      }, 3000);
    }
  };
  
  const curlExample = `curl -X POST 'https://veyraxapp.com/tool-call/${imageName}/methodName' \\
  -H 'VEYRAX_API_KEY: YOUR_API_KEY' \\
  -H 'Content-Type: application/json' \\
  -d '{
    "param1": "value1",
    "param2": "value2"
  }'`;

  const exampleRequest = `{
  "param1": "value1",
  "param2": "value2"
}`;

  const exampleResponse = `{
  "status": "success",
  "data": {
    "result": "Example response from ${imageName}",
    "timestamp": "2023-11-09T12:34:56Z"
  }
}`;
  
  const handleCopyRequest = () => {
    navigator.clipboard.writeText(curlExample);
    setCopiedRequest(true);
    setTimeout(() => setCopiedRequest(false), 2000);
  };
  
  const handleCopyResponse = () => {
    navigator.clipboard.writeText(exampleResponse);
    setCopiedResponse(true);
    setTimeout(() => setCopiedResponse(false), 2000);
  };
  
  return (
    <>
      {/* Installation Card */}
      <div className="bg-white dark:bg-gray-900 rounded-md border border-gray-200 dark:border-gray-800 mb-6">
        <div className="p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex flex-col">
              <h2 className="text-xl font-medium text-foreground">Installation</h2>
              <p className="text-muted-foreground mt-1">Connect to use this MCP in your applications</p>
            </div>
            <Button 
              onClick={handleConnect}
              disabled={isConnected}
            >
              {isConnected ? (
                <>
                  <Check className="mr-2 h-4 w-4" />
                  Connected
                </>
              ) : (
                'Connect'
              )}
            </Button>
          </div>
        </div>
      </div>
      
      {/* Usage Card */}
      <div className="bg-white dark:bg-gray-900 rounded-md border border-gray-200 dark:border-gray-800">
        <div className="p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex flex-col">
              <h2 className="text-xl font-medium text-foreground">Usage</h2>
              <p className="text-muted-foreground mt-1">How to use this MCP in your application</p>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-1 gap-6">
            <div>
              <div className="flex justify-between items-center mb-2">
                <h5 className="text-sm font-medium text-foreground">Request Example</h5>
                <button 
                  onClick={handleCopyRequest}
                  className="text-muted-foreground hover:text-foreground transition-colors p-1 rounded-md hover:bg-accent"
                  aria-label="Copy request"
                >
                  {copiedRequest ? (
                    <CheckIcon className="h-4 w-4 text-green-500" />
                  ) : (
                    <CopyIcon className="h-4 w-4" />
                  )}
                </button>
              </div>
              <div className="rounded-md overflow-hidden">
                <SyntaxHighlighter 
                  language="bash" 
                  style={vscDarkPlus}
                  customStyle={{ margin: 0, borderRadius: '0.375rem' }}
                >
                  {curlExample}
                </SyntaxHighlighter>
              </div>
            </div>

            <div>
              <div className="flex justify-between items-center mb-2">
                <h5 className="text-sm font-medium text-foreground">Example Response</h5>
                <button 
                  onClick={handleCopyResponse}
                  className="text-muted-foreground hover:text-foreground transition-colors p-1 rounded-md hover:bg-accent"
                  aria-label="Copy response"
                >
                  {copiedResponse ? (
                    <CheckIcon className="h-4 w-4 text-green-500" />
                  ) : (
                    <CopyIcon className="h-4 w-4" />
                  )}
                </button>
              </div>
              <div className="rounded-md overflow-hidden">
                <SyntaxHighlighter 
                  language="json" 
                  style={vscDarkPlus}
                  customStyle={{ margin: 0, borderRadius: '0.375rem' }}
                >
                  {exampleResponse}
                </SyntaxHighlighter>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* MCP Manage Dialog */}
      {showManageDialog && (
        <McpManage
          imageName={imageName}
          open={showManageDialog}
          onClose={handleManageClose}
          predefinedEnv={mcpDetails?.env || {}}
        />
      )}
    </>
  );
} 