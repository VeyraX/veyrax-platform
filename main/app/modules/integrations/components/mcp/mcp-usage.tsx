import { useState } from "react";
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { ArrowUpRight, CheckIcon, CopyIcon, AlertCircle, LogIn } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { McpDetails, UserMcpEnvironment } from "@/app/modules/integrations/api/types.integrations.mcp";
import { generateApiKey } from "@/app/modules/settings/api/api.settings";

interface McpUsageProps {
  imageName: string;
  mcpDetails?: McpDetails | null;
  userEnvironment?: UserMcpEnvironment | null;
  isConnected?: boolean;
  apiKey?: string;
  onApiKeyGenerated?: (apiKey: string) => void;
  onLogin?: () => void;
  isPublic?: boolean;
}

export function McpUsage({ 
  imageName, 
  mcpDetails, 
  userEnvironment, 
  isConnected = false,
  apiKey,
  onApiKeyGenerated,
  onLogin,
  isPublic = false
}: McpUsageProps) {
  const [copiedCommand, setCopiedCommand] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('cursor');
  const [isGeneratingApiKey, setIsGeneratingApiKey] = useState(false);
  const [copiedJson, setCopiedJson] = useState(false);
  
  const processId = userEnvironment?.process_id || null;
  
  const extractedPart = processId ? processId.split('-')[0] : null;

  const jsonConfig = {
    [`veyrax-${extractedPart || "process"}`]: {
      "command": "npx",
      "args": [
        "-y",
        "@veyrax/mcp-cli",
        "deploy",
        "--sse",
        `http://${processId || "[process_id]"}.mcp.veyraxapp.com/sse`,
        "--header",
        `VEYRAX_API_KEY:${apiKey || "API_KEY"}`
      ]
    }
  };

  const jsonConfigStr = JSON.stringify(jsonConfig, null, 2);
  
  const mcpCommands = {
    cursor: userEnvironment && processId && apiKey ? 
      `npx @veyrax/mcp-cli install ${processId} ${apiKey} --client cursor` : 
      `npx @veyrax/mcp-cli install [process-id] [api-key] --client cursor`,
    claude: userEnvironment && processId && apiKey ? 
      `npx @veyrax/mcp-cli install ${processId} ${apiKey} --client claude` : 
      `npx @veyrax/mcp-cli install [process-id] [api-key] --client claude`,
    windsurf: userEnvironment && processId && apiKey ? 
      `npx @veyrax/mcp-cli install ${processId} ${apiKey} --client windsurf` : 
      `npx @veyrax/mcp-cli install [process-id] [api-key] --client windsurf`,
    cline: userEnvironment && processId && apiKey ? 
      `npx @veyrax/mcp-cli install ${processId} ${apiKey} --client cline` : 
      `npx @veyrax/mcp-cli install [process-id] [api-key] --client cline`,
  };

  const handleCopyCommand = (command: string) => {
    navigator.clipboard.writeText(command);
    setCopiedCommand(command);
    setTimeout(() => setCopiedCommand(null), 2000);
  };

  const handleCopyJson = () => {
    navigator.clipboard.writeText(jsonConfigStr);
    setCopiedJson(true);
    setTimeout(() => setCopiedJson(false), 2000);
  };
  
  const handleGenerateApiKey = async () => {
    setIsGeneratingApiKey(true);
    try {
      const newApiKey = await generateApiKey();
      if (newApiKey && onApiKeyGenerated) {
        onApiKeyGenerated(newApiKey.api_key);
      }
    } catch (error) {
      console.error("Failed to generate API key:", error);
    } finally {
      setIsGeneratingApiKey(false);
    }
  };

  const shouldShowSseUrl = !isPublic && apiKey && isConnected && processId;

  return (
    <div className="bg-white dark:bg-gray-900 rounded-md border border-gray-200 dark:border-gray-800">
      <div className="p-6 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex flex-col">
            <h2 className="text-xl font-medium text-foreground">Installation</h2>
            <p className="text-muted-foreground mt-1">Run the following command in terminal to install MCP in following clients:</p>
          </div>
        </div>

        {!isPublic && apiKey === "" ? (
          <Alert className="bg-amber-50 border-amber-200 dark:bg-amber-950/20 dark:border-amber-800/50 flex items-center justify-between">
            <div className="flex items-center">
              <AlertCircle className="h-4 w-4 text-amber-500" />
              <AlertDescription className="ml-2 text-amber-700 dark:text-amber-400">
                You need an API key to use MCP.
              </AlertDescription>
            </div>
            <Button 
              variant="outline" 
              size="sm" 
              onClick={handleGenerateApiKey}
              disabled={isGeneratingApiKey}
            >
              {isGeneratingApiKey ? "Generating..." : "Generate"}
            </Button>
          </Alert>
        ) : null}

        {shouldShowSseUrl ? (
          <Tabs defaultValue="cursor" className="w-full">
            <TabsList className="h-auto gap-2 rounded-none bg-transparent px-0 py-1 text-foreground mb-4">
              <TabsTrigger 
                className="relative after:absolute after:inset-x-0 after:bottom-0 after:-mb-1 after:h-0.5 hover:bg-accent hover:text-foreground data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:after:bg-primary data-[state=active]:hover:bg-accent" 
                value="cursor"
                onClick={() => setActiveTab('cursor')}
              >
                Cursor
              </TabsTrigger>
              <TabsTrigger 
                className="relative after:absolute after:inset-x-0 after:bottom-0 after:-mb-1 after:h-0.5 hover:bg-accent hover:text-foreground data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:after:bg-primary data-[state=active]:hover:bg-accent" 
                value="claude"
                onClick={() => setActiveTab('claude')}
              >
                Claude
              </TabsTrigger>
              <TabsTrigger 
                className="relative after:absolute after:inset-x-0 after:bottom-0 after:-mb-1 after:h-0.5 hover:bg-accent hover:text-foreground data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:after:bg-primary data-[state=active]:hover:bg-accent" 
                value="windsurf"
                onClick={() => setActiveTab('windsurf')}
              >
                Windsurf
              </TabsTrigger>
              <TabsTrigger 
                className="relative after:absolute after:inset-x-0 after:bottom-0 after:-mb-1 after:h-0.5 hover:bg-accent hover:text-foreground data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:after:bg-primary data-[state=active]:hover:bg-accent" 
                value="cline"
                onClick={() => setActiveTab('cline')}
              >
                Cline
              </TabsTrigger>
              <TabsTrigger 
                className="relative after:absolute after:inset-x-0 after:bottom-0 after:-mb-1 after:h-0.5 hover:bg-accent hover:text-foreground data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:after:bg-primary data-[state=active]:hover:bg-accent" 
                value="json-config"
                onClick={() => setActiveTab('json-config')}
              >
                JSON Config
              </TabsTrigger>
            </TabsList>
            
            {Object.entries(mcpCommands).map(([key, command]) => (
              <TabsContent key={key} value={key} className="mt-0">
                <div className="flex gap-2 items-center">
                  <div className="relative flex-1 font-mono text-sm p-3 bg-gray-50 dark:bg-gray-800 rounded-md">
                    {command}
                  </div>
                  <Button 
                    variant="outline" 
                    size="icon" 
                    onClick={() => handleCopyCommand(command)}
                  >
                    {copiedCommand === command ? 
                      <CheckIcon className="h-4 w-4" /> : 
                      <CopyIcon className="h-4 w-4" />}
                  </Button>
                </div>
              </TabsContent>
            ))}
            
            <TabsContent value="json-config" className="mt-0">
              <div className="flex gap-2 items-center">
                <div className="relative flex-1 font-mono text-sm p-3 bg-gray-50 dark:bg-gray-800 rounded-md overflow-auto whitespace-pre">
                  {jsonConfigStr}
                </div>
                <Button 
                  variant="outline" 
                  size="icon" 
                  onClick={handleCopyJson}
                >
                  {copiedJson ? 
                    <CheckIcon className="h-4 w-4" /> : 
                    <CopyIcon className="h-4 w-4" />}
                </Button>
              </div>
            </TabsContent>
          </Tabs>
        ) : (
          <div className="flex items-center justify-center p-6 border rounded-lg bg-gray-50 dark:bg-gray-800/50">
            <p className="text-sm text-muted-foreground">
              {isPublic 
                ? "Login to view installation commands." 
                : !apiKey 
                  ? "Login to view installation commands."
                  : "Connect MCP to view installation commands."}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
