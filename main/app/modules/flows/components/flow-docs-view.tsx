import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { CheckIcon, CopyIcon } from "lucide-react";
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { toast } from "sonner";

interface ApiEndpoint {
  name: string;
  value: string;
  example: string | ((flowId: string) => string);
  responseSchema: string;
}

interface ApiDocumentationProps {
  flowId: string;
  endpoints?: ApiEndpoint[];
}

const defaultEndpoints: ApiEndpoint[] = [
  {
    name: "Get All Flows",
    value: "get-flows",
    example: `curl -X GET "https://veyraxapp.com/get-flows" \\
-H "Content-Type: application/json" \\
-H "Authorization: VEYRAX_API_KEY"`,
    responseSchema: `{
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
}`
  },
  {
    name: "Get Flow by ID",
    value: "get-flow",
    example: (flowId: string) => `curl -X GET "https://veyraxapp.com/flow/get-flow/${flowId}" \\
-H "Content-Type: application/json" \\
-H "Authorization: VEYRAX_API_KEY"`,
    responseSchema: `{
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
}`
  }
];

export function ApiDocumentation({ flowId, endpoints = defaultEndpoints }: ApiDocumentationProps) {
  const [copiedStates, setCopiedStates] = useState<Record<string, boolean>>({});

  const handleCopy = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedStates(prev => ({ ...prev, [id]: true }));
    
    setTimeout(() => {
      setCopiedStates(prev => ({ ...prev, [id]: false }));
    }, 2000);
    
    toast.success("Copied to clipboard");
  };

  return (
    <div className="bg-white rounded-md border p-6">
      <Tabs defaultValue={endpoints[0].value} className="w-full">
        <div className="flex justify-end w-full mb-4">
          <TabsList className="h-auto gap-4 rounded-none bg-transparent px-0 py-0 text-foreground">
            {endpoints.map((endpoint) => (
              <TabsTrigger
                key={endpoint.value}
                className="relative after:absolute after:inset-x-0 after:bottom-0 after:-mb-1 after:h-0.5 hover:bg-accent hover:text-foreground data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:after:bg-primary data-[state=active]:hover:bg-accent"
                value={endpoint.value}
              >
                {endpoint.name}
              </TabsTrigger>
            ))}
          </TabsList>
        </div>

        {endpoints.map((endpoint) => (
          <TabsContent key={endpoint.value} value={endpoint.value} className="mt-0">
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-sm font-medium">Example</h3>
                <Button
                  onClick={() => handleCopy(
                    typeof endpoint.example === 'function' 
                      ? endpoint.example(flowId) 
                      : endpoint.example,
                    `${endpoint.value}-example`
                  )}
                  size="sm"
                  variant="ghost"
                  className="h-6 w-6"
                >
                  {copiedStates[`${endpoint.value}-example`] ? (
                    <CheckIcon className="h-4 w-4" />
                  ) : (
                    <CopyIcon className="h-4 w-4" />
                  )}
                </Button>
              </div>
              <SyntaxHighlighter
                language="bash"
                style={vscDarkPlus}
                customStyle={{ margin: 0, borderRadius: '0.375rem' }}
              >
                {typeof endpoint.example === 'function' 
                  ? endpoint.example(flowId) 
                  : endpoint.example}
              </SyntaxHighlighter>

              <div className="flex justify-between items-center mt-6">
                <h3 className="text-sm font-medium">Response Schema</h3>
                <Button
                  onClick={() => handleCopy(endpoint.responseSchema, `${endpoint.value}-response`)}
                  size="sm"
                  variant="ghost"
                  className="h-6 w-6"
                >
                  {copiedStates[`${endpoint.value}-response`] ? (
                    <CheckIcon className="h-4 w-4" />
                  ) : (
                    <CopyIcon className="h-4 w-4" />
                  )}
                </Button>
              </div>
              <SyntaxHighlighter
                language="javascript"
                style={vscDarkPlus}
                customStyle={{ margin: 0, borderRadius: '0.375rem' }}
              >
                {endpoint.responseSchema}
              </SyntaxHighlighter>
            </div>
          </TabsContent>
        ))}
      </Tabs>
    </div>
  );
} 