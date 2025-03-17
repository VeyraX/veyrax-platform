'use client';

import { Separator } from "@/components/ui/separator"
import { Button } from "@/components/ui/button"
import { useState } from "react"
import { UserApiKey } from "../api/types.settings"
import { Input } from "@/components/ui/input"
import { Copy, Check, Clipboard } from "lucide-react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { AlertCircle } from "lucide-react"
import { Files, Ticket, ArrowUpRight } from "lucide-react"
import FeedbackDialog from "@/app/modules/general/components/feedback-dialog"

interface MCPSettingsProps {
  apiKey: UserApiKey | null;
  onGenerateApiKey?: () => Promise<UserApiKey | null>;
}

export default function MCPSettings({ apiKey, onGenerateApiKey }: MCPSettingsProps) {
  const [copiedCommand, setCopiedCommand] = useState<string | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [activeTab, setActiveTab] = useState('cursor')
  const [feedbackDialogOpen, setFeedbackDialogOpen] = useState(false)

  const mcpCommands = {
    cursor: {
      Windows: apiKey ? 
        `C:\\Windows\\System32\\cmd.exe /c npx -y @smithery/cli@latest run @VeyraX/veyrax-mcp --config "{\\"VEYRAX_API_KEY\\":\\"${apiKey.api_key}\\"}"` : 
        `C:\\Windows\\System32\\cmd.exe /c npx -y @smithery/cli@latest run @VeyraX/veyrax-mcp --config "{\\"VEYRAX_API_KEY\\":\\"VEYRAX_API_KEY\\"}"`,
      MacOS: apiKey ? 
        `npx -y @smithery/cli@latest run @VeyraX/veyrax-mcp --config "{\\"VEYRAX_API_KEY\\":\\"${apiKey.api_key}\\"}"` : 
        `npx -y @smithery/cli@latest run @VeyraX/veyrax-mcp --config "{\\"VEYRAX_API_KEY\\":\\"VEYRAX_API_KEY\\"}"`
    },
    claude: apiKey ? 
      `npx -y @smithery/cli@latest install @VeyraX/veyrax-mcp --client claude --config "{\\"VEYRAX_API_KEY\\":\\"${apiKey.api_key}\\"}"` :
      `npx -y @smithery/cli@latest install @VeyraX/veyrax-mcp --client claude`,
    windsurf: apiKey ? 
      `npx -y @smithery/cli@latest install @VeyraX/veyrax-mcp --client windsurf --config "{\\"VEYRAX_API_KEY\\":\\"${apiKey.api_key}\\"}"` :
      `npx -y @smithery/cli@latest install @VeyraX/veyrax-mcp --client windsurf`,
    cline: apiKey ? 
      `npx -y @smithery/cli@latest install @VeyraX/veyrax-mcp --client cline --config "{\\"VEYRAX_API_KEY\\":\\"${apiKey.api_key}\\"}"` :
      `npx -y @smithery/cli@latest install @VeyraX/veyrax-mcp --client cline`,
  }

  const handleCopyCommand = (command: string) => {
    navigator.clipboard.writeText(command)
    setCopiedCommand(command)
    setTimeout(() => setCopiedCommand(null), 2000)
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold tracking-tight">MCP Configuration</h2>
        <p className="text-sm text-muted-foreground">
          Copy and paste these commands to set up VeyraX MCP with different clients.
        </p>
      </div>

      <Separator />

      {!apiKey && (
        <Alert className="mb-4 bg-amber-50 border-amber-200 dark:bg-amber-950/20 dark:border-amber-800/50 flex items-center justify-between">
          <div className="flex items-center">
            <AlertCircle className="h-4 w-4 text-amber-500" />
            <AlertDescription className="ml-2 text-amber-700 dark:text-amber-400">
              You need an API key to use MCP.
            </AlertDescription>
          </div>
          {onGenerateApiKey && (
            <Button 
              variant="outline" 
              size="sm" 
              onClick={async () => {
                setIsGenerating(true);
                await onGenerateApiKey();
                setIsGenerating(false);
              }}
              disabled={isGenerating}
            >
              {isGenerating ? "Generating..." : "Generate"}
            </Button>
          )}
        </Alert>
      )}

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
        </TabsList>
        
        {Object.entries(mcpCommands).map(([key, command]) => (
          <TabsContent key={key} value={key} className="mt-0">
            <div className="p-6 border rounded-lg">
              <div className="mb-4">
                <h3 className="text-lg font-semibold capitalize">{key} Setup</h3>
                <p className="text-sm text-muted-foreground">
                  Configure VeyraX MCP with your API key
                </p>
              </div>
              
              {key === 'cursor' ? (
                <>
                  <div className="mb-4">
                    <h4 className="text-sm font-medium mb-2">Windows</h4>
                    <div className="flex gap-2">
                      <div className="relative flex-1">
                        <Input
                          value={(command as {Windows: string; MacOS: string}).Windows}
                          readOnly
                          className="pr-10 font-mono text-sm"
                        />
                      </div>
                      <Button 
                        variant="outline" 
                        size="icon" 
                        onClick={() => handleCopyCommand((command as {Windows: string; MacOS: string}).Windows)}
                      >
                        {copiedCommand === (command as {Windows: string; MacOS: string}).Windows ? 
                          <Check className="h-4 w-4" /> : 
                          <Copy className="h-4 w-4" />}
                      </Button>
                    </div>
                  </div>
                  <div>
                    <h4 className="text-sm font-medium mb-2">MacOS</h4>
                    <div className="flex gap-2">
                      <div className="relative flex-1">
                        <Input
                          value={(command as {Windows: string; MacOS: string}).MacOS}
                          readOnly
                          className="pr-10 font-mono text-sm"
                        />
                      </div>
                      <Button 
                        variant="outline" 
                        size="icon" 
                        onClick={() => handleCopyCommand((command as {Windows: string; MacOS: string}).MacOS)}
                      >
                        {copiedCommand === (command as {Windows: string; MacOS: string}).MacOS ? 
                          <Check className="h-4 w-4" /> : 
                          <Copy className="h-4 w-4" />}
                      </Button>
                    </div>
                  </div>
                </>
              ) : (
                <div className="flex gap-2">
                  <div className="relative flex-1">
                    <Input
                      value={command as string}
                      readOnly
                      className="pr-10 font-mono text-sm"
                    />
                  </div>
                  <Button 
                    variant="outline" 
                    size="icon" 
                    onClick={() => handleCopyCommand(command as string)}
                  >
                    {copiedCommand === command ? 
                      <Check className="h-4 w-4" /> : 
                      <Copy className="h-4 w-4" />}
                  </Button>
                </div>
              )}
              
              {key === 'config' && !apiKey && (
                <p className="text-sm text-amber-500 mt-2">
                  Note: Generate an API key first to get a valid configuration command.
                </p>
              )}
            </div>
          </TabsContent>
        ))}
      </Tabs>

      <Separator />

      <div className="mt-8">
        <div className="p-6 border rounded-lg">
          <div className="mb-4">
            <h3 className="text-lg font-semibold">Installation Guide</h3>
            <p className="text-sm text-muted-foreground">
              Need help with installation? Check our comprehensive documentation.
            </p>
          </div>
          
          <div className="flex gap-2">
            <Button 
              variant="outline"
              onClick={() => window.open(`https://docs.veyrax.com/mcp/${activeTab}`, '_blank')}
            >
              Open Docs
              <ArrowUpRight className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              onClick={() => setFeedbackDialogOpen(true)}
            >
              Ask a Question
            </Button>
          </div>
        </div>
      </div>

      <FeedbackDialog 
        open={feedbackDialogOpen} 
        onOpenChange={setFeedbackDialogOpen} 
      />
    </div>
  )
}