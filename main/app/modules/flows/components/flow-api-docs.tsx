import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { CheckIcon, CopyIcon } from "lucide-react";
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { QuickStart } from "./quick-start";

interface FlowApiDocsProps {
  flowName: string;
  flowId: string;
  isOwner: boolean;
  isAuthenticated: boolean;
}

export function FlowApiDocs({ flowName, flowId, isOwner, isAuthenticated }: FlowApiDocsProps) {
  const [copiedStates, setCopiedStates] = useState<Record<string, boolean>>({});

  const getFlowsExample = `curl -X GET "https://veyaraxapp.com/api/flows" \\
-H "Content-Type: application/json" \\
-H "Authorization: VEYRAX_API_KEY"`;

  const getFlowExample = `curl -X GET "https://veyaraxapp.com/api/flows/${flowId}" \\
-H "Content-Type: application/json" \\
-H "Authorization: VEYRAX_API_KEY"`;

  return (
    <div className="flex flex-col space-y-6">
      <QuickStart 
        flowName={flowName} 
        isOwner={isOwner}
        isAuthenticated={isAuthenticated}
      />
      
      <div className="bg-white rounded-md border p-6">
        <Tabs defaultValue="get-flows" className="w-full">
          <div className="flex justify-end w-full mb-4">
            <TabsList className="h-auto gap-4 rounded-none bg-transparent px-0 py-0 text-foreground">
              <TabsTrigger 
                className="relative after:absolute after:inset-x-0 after:bottom-0 after:-mb-1 after:h-0.5 hover:bg-accent hover:text-foreground data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:after:bg-primary data-[state=active]:hover:bg-accent" 
                value="get-flows"
              >
                Get All Flows
              </TabsTrigger>
              <TabsTrigger 
                className="relative after:absolute after:inset-x-0 after:bottom-0 after:-mb-1 after:h-0.5 hover:bg-accent hover:text-foreground data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:after:bg-primary data-[state=active]:hover:bg-accent" 
                value="get-flow"
              >
                Get Flow by ID
              </TabsTrigger>
            </TabsList>
          </div>

          <TabsContent value="get-flows" className="mt-0">
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-sm font-medium">Example</h3>
                <Button 
                  onClick={() => {
                    navigator.clipboard.writeText(getFlowsExample);
                    setCopiedStates(prev => ({ ...prev, "get-flows": true }));
                    setTimeout(() => {
                      setCopiedStates(prev => ({ ...prev, "get-flows": false }));
                    }, 2000);
                  }}
                  size="sm"
                  variant="ghost"
                  className="h-6 w-6"
                >
                  {copiedStates["get-flows"] ? <CheckIcon className="h-4 w-4" /> : <CopyIcon className="h-4 w-4" />}
                </Button>
              </div>
              <SyntaxHighlighter 
                language="bash" 
                style={vscDarkPlus}
                customStyle={{ margin: 0, borderRadius: '0.375rem' }}
              >
                {getFlowsExample}
              </SyntaxHighlighter>
              
              <div className="flex justify-between items-center mt-6">
                <h3 className="text-sm font-medium">Response Schema</h3>
                <Button 
                  onClick={() => {
                    navigator.clipboard.writeText(`{
  "flows": [{
    "id": "string",
    "name": "string",
    "plain_description": "string",
    "available_actions": [
      {
        "provider_slug": "string",
        "action_slug": "string",
        "input_schema": {...},
        "output_schema": {...}
      }
    ]
  }]
}`);
                    setCopiedStates(prev => ({ ...prev, "get-flows-response": true }));
                    setTimeout(() => {
                      setCopiedStates(prev => ({ ...prev, "get-flows-response": false }));
                    }, 2000);
                  }}
                  size="sm"
                  variant="ghost"
                  className="h-6 w-6"
                >
                  {copiedStates["get-flows-response"] ? <CheckIcon className="h-4 w-4" /> : <CopyIcon className="h-4 w-4" />}
                </Button>
              </div>
              <SyntaxHighlighter 
                language="javascript" 
                style={vscDarkPlus}
                customStyle={{ margin: 0, borderRadius: '0.375rem' }}
              >
                {`{
  "flows": [{
    "id": "string",
    "name": "string",
    "plain_description": "string",
    "available_actions": [
      {
        "provider_slug": "string",
        "action_slug": "string",
        "input_schema": {...},
        "output_schema": {...}
      }
    ]
  }]
}`}
              </SyntaxHighlighter>
            </div>
          </TabsContent>

          <TabsContent value="get-flow" className="mt-0">
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-sm font-medium">Example</h3>
                <Button 
                  onClick={() => {
                    navigator.clipboard.writeText(getFlowExample);
                    setCopiedStates(prev => ({ ...prev, "get-flow": true }));
                    setTimeout(() => {
                      setCopiedStates(prev => ({ ...prev, "get-flow": false }));
                    }, 2000);
                  }}
                  size="sm"
                  variant="ghost"
                  className="h-6 w-6"
                >
                  {copiedStates["get-flow"] ? <CheckIcon className="h-4 w-4" /> : <CopyIcon className="h-4 w-4" />}
                </Button>
              </div>
              <SyntaxHighlighter 
                language="bash" 
                style={vscDarkPlus}
                customStyle={{ margin: 0, borderRadius: '0.375rem' }}
              >
                {getFlowExample}
              </SyntaxHighlighter>
              
              <div className="flex justify-between items-center mt-6">
                <h3 className="text-sm font-medium">Response Schema</h3>
                <Button 
                  onClick={() => {
                    navigator.clipboard.writeText(`{
  "flows": {
    "id": "string",
    "name": "string",
    "plain_description": "string",
    "available_actions": [
      {
        "provider_slug": "string",
        "action_slug": "string",
        "input_schema": {...},
        "output_schema": {...}
      }
    ]
  }
}`);
                    setCopiedStates(prev => ({ ...prev, "get-flow-response": true }));
                    setTimeout(() => {
                      setCopiedStates(prev => ({ ...prev, "get-flow-response": false }));
                    }, 2000);
                  }}
                  size="sm"
                  variant="ghost"
                  className="h-6 w-6"
                >
                  {copiedStates["get-flow-response"] ? <CheckIcon className="h-4 w-4" /> : <CopyIcon className="h-4 w-4" />}
                </Button>
              </div>
              <SyntaxHighlighter 
                language="javascript" 
                style={vscDarkPlus}
                customStyle={{ margin: 0, borderRadius: '0.375rem' }}
              >
                {`{
  "flows": {
    "id": "string",
    "name": "string",
    "plain_description": "string",
    "available_actions": [
      {
        "provider_slug": "string",
        "action_slug": "string",
        "input_schema": {...},
        "output_schema": {...}
      }
    ]
  }
}`}
              </SyntaxHighlighter>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
} 