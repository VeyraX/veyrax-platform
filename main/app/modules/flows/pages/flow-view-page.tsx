"use client";

import { useEffect, useState } from "react";
import { getFlowById, getUserActions } from "../api/api.flows";
import { useRouter } from "next/navigation";
import { FlowHeader } from "../components/header";
import { ToolsList } from "../components/flow-description-tool-detector";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { Code, Copy, Edit, Terminal, Info, Play, CheckIcon, CopyIcon } from "lucide-react";
import { toast } from "sonner";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { isEmptyHTML } from "../components/flow-description-html";
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

function cleanHtml(html: string): string {
  const parser = new DOMParser();
  const doc = parser.parseFromString(html, 'text/html');

  doc.querySelectorAll('h1, h2, h3, h4, h5, h6').forEach(heading => {
    heading.classList.add('font-semibold', 'mb-2', 'mt-4');
    
    if (heading.tagName.toLowerCase() === 'h3') {
      heading.classList.add('text-lg');
    }
  });
  
  doc.querySelectorAll('ol').forEach(list => {
    list.classList.add('list-decimal', 'pl-5', 'my-3');
  });
  
  doc.querySelectorAll('ul').forEach(list => {
    list.classList.add('list-disc', 'pl-5', 'my-3');
  });
  
  doc.querySelectorAll('li').forEach(item => {
    item.classList.add('ml-2', 'my-3');
  });
  
  return doc.body.innerHTML;
}

interface FlowViewPageProps {
  flowId: string;
}

export default function FlowViewPage({ flowId }: FlowViewPageProps) {
  const router = useRouter();
  const [flow, setFlow] = useState<any>(null);
  const [actions, setActions] = useState<any[]>([]);
  const [isOwner, setIsOwner] = useState(false);
  const [isLoadingFlow, setIsLoadingFlow] = useState(true);
  const [usedTools, setUsedTools] = useState<any[]>([]);
  const [copiedStates, setCopiedStates] = useState<Record<string, boolean>>({});
  
  useEffect(() => {
    const loadFlow = async () => {
      try {
        setIsLoadingFlow(true);
        
        const flowData = await getFlowById(flowId);
        if (flowData) {
          setFlow(flowData);
          setIsOwner(true); 
        }
        
        const actionsData = await getUserActions();
        setActions(actionsData);
        
      } catch (error) {
        console.error('Error loading flow:', error);
      } finally {
        setIsLoadingFlow(false);
      }
    };
    
    if (flowId) {
      loadFlow();
    }
  }, [flowId]);
  
  useEffect(() => {
    if (flow && actions.length > 0 && flow.description) {
      try {
        const parser = new DOMParser();
        const doc = parser.parseFromString(flow.description, 'text/html');
        const actionElements = doc.querySelectorAll('.action-item');
        
        const detectedTools = new Map();
        
        actionElements.forEach(element => {
          const providerName = element.getAttribute('data-provider');
          const actionName = element.getAttribute('data-action');
          
          if (providerName && actionName) {
            const matchingAction = actions.find(a => 
              a.provider_name === providerName && a.action_name === actionName
            );
            
            if (matchingAction) {
              detectedTools.set(matchingAction.provider_id, {
                provider_id: matchingAction.provider_id,
                provider_name: matchingAction.provider_name,
                logo_url: matchingAction.logo_url
              });
            }
          }
        });
        
        setUsedTools(Array.from(detectedTools.values()));
      } catch (error) {
        console.error('Error detecting tools:', error);
      }
    }
  }, [flow, actions]);
  
  const handleEdit = () => {
    router.push(`/flow/${flowId}/edit`);
  };
  
  const handleClone = () => {
    // Logic to clone the flow would go here
    toast.success("Flow cloned", {
      description: "A copy of this flow has been added to your flows"
    });
  };
  
  const handleBack = () => {
    router.back();
  };
  
  const handleCopy = (text: string, id: string) => {
    navigator.clipboard.writeText(text).then(() => {
      setCopiedStates(prev => ({ ...prev, [id]: true }));
      
      setTimeout(() => {
        setCopiedStates(prev => ({ ...prev, [id]: false }));
      }, 2000);
      
      toast.success("Copied", {
        description: "Code copied to clipboard"
      });
    });
  };
  
  if (isLoadingFlow) {
    return (
      <div className="h-screen overflow-hidden flex flex-col">
        <div className="flex items-center justify-between w-full px-4 py-2 bg-white border-b border-gray-200">
          <div className="flex items-center gap-2">
            <Skeleton className="w-6 h-6 rounded-full" />
            <Skeleton className="w-40 h-5" />
          </div>
          <Skeleton className="w-20 h-7 rounded-full" />
        </div>
        
        <div className="flex-1 overflow-hidden p-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="space-y-6">
              <div className="bg-white rounded-md border p-6 space-y-4">
                <Skeleton className="w-32 h-6" />
                <Skeleton className="w-full h-40" />
              </div>
              
              <div className="bg-white rounded-md border p-6 space-y-4">
                <Skeleton className="w-24 h-6" />
                <Skeleton className="w-full h-20" />
              </div>
            </div>
            
            <div className="flex flex-col">
              <div className="flex justify-end mb-4">
                <Skeleton className="w-64 h-8" />
              </div>
              <div className="bg-white rounded-md border p-6">
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <Skeleton className="w-32 h-6" />
                    <Skeleton className="w-8 h-8 rounded-full" />
                  </div>
                  <Skeleton className="w-full h-40" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }
  
  if (!flow) {
    return (
      <div className="h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-semibold">Flow not found</h2>
          <p className="text-muted-foreground mt-2">This flow might have been deleted or you don't have access to it.</p>
          <Button className="mt-4" onClick={() => router.push('/flows')}>Go back to flows</Button>
        </div>
      </div>
    );
  }

  const requestId = `request-${flow.id}`;
  const responseId = `response-${flow.id}`;
  const pythonId = `python-${flow.id}`;
  const requestText = `fetch('/api/flow/run', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    flowId: '${flow.id}',
    inputs: {
      // Add any required inputs here
    }
  })
})`;

  const curlText = `curl -X POST "https://your-domain.com/api/flow/run" \\
-H "Content-Type: application/json" \\
-d '{"flowId":"${flow.id}","inputs":{}}'`;
  
  return (
    <div className="flex flex-col h-screen overflow-hidden">
      <FlowHeader 
        flowName={flow.name || "Flow"} 
        onBack={handleBack}
        isLoading={isLoadingFlow}
        flowId={flow.id}
        isOwner={isOwner}
      />
      
      <div className="flex-1 overflow-auto">
        <div className="w-full px-6 py-6">

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="space-y-6">
              <div className="bg-white rounded-md border p-6 space-y-4">
                <h2 className="text-xl font-medium text-foreground flex items-center gap-2">
                  Overview
                </h2>
                
                {flow.description && !isEmptyHTML(flow.description) ? (
                  <div className="prose prose-sm md:prose-base max-w-none text-foreground prose-headings:font-semibold prose-h1:text-2xl prose-h2:text-xl prose-h3:text-lg prose-p:text-foreground/90 prose-ul:list-disc prose-ol:list-decimal prose-ul:pl-5 prose-ol:pl-5 prose-li:my-3">
                    <div dangerouslySetInnerHTML={{ __html: cleanHtml(flow.description) }} />
                  </div>
                ) : (
                  <div className="text-muted-foreground italic">
                    No description available for this flow.
                  </div>
                )}
              </div>
              
              <div className="bg-white rounded-md border p-6 space-y-4">
                <h2 className="text-xl font-medium text-foreground">Tools</h2>
                <div>
                  <ToolsList tools={usedTools} />
                </div>
              </div>
            </div>
            
            <div className="flex flex-col">
              <div className="bg-white rounded-md border p-6">
                <Tabs defaultValue="javascript" className="w-full">
                  <div className="flex justify-end w-full mb-4">
                    <TabsList className="h-auto gap-4 rounded-none bg-transparent px-0 py-0 text-foreground">
                      <TabsTrigger 
                        className="relative after:absolute after:inset-x-0 after:bottom-0 after:-mb-1 after:h-0.5 hover:bg-accent hover:text-foreground data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:after:bg-primary data-[state=active]:hover:bg-accent" 
                        value="curl"
                      >
                        cURL
                      </TabsTrigger>
                      <TabsTrigger 
                        className="relative after:absolute after:inset-x-0 after:bottom-0 after:-mb-1 after:h-0.5 hover:bg-accent hover:text-foreground data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:after:bg-primary data-[state=active]:hover:bg-accent" 
                        value="python"
                      >
                        Python
                      </TabsTrigger>
                      <TabsTrigger 
                        className="relative after:absolute after:inset-x-0 after:bottom-0 after:-mb-1 after:h-0.5 hover:bg-accent hover:text-foreground data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:after:bg-primary data-[state=active]:hover:bg-accent" 
                        value="javascript"
                      >
                        IDE
                      </TabsTrigger>
                    </TabsList>
                  </div>

                  <TabsContent value="javascript" className="mt-0 w-full">
                    <div className="space-y-6">
                      <div>
                        <div className="flex justify-between items-center mb-2">
                          <h3 className="text-sm font-medium text-foreground flex items-center gap-2">
                            <Code size={18} />
                            JavaScript
                          </h3>
                          <button 
                            onClick={() => handleCopy(requestText, requestId)}
                            className="text-muted-foreground hover:text-foreground transition-colors p-1 rounded-md hover:bg-accent"
                            aria-label="Copy request"
                          >
                            {copiedStates[requestId] ? (
                              <CheckIcon className="h-4 w-4" />
                            ) : (
                              <CopyIcon className="h-4 w-4" />
                            )}
                          </button>
                        </div>
                        <div className="rounded-md overflow-hidden">
                          <SyntaxHighlighter 
                            language="javascript" 
                            style={vscDarkPlus}
                            customStyle={{ margin: 0, borderRadius: '0.375rem' }}
                          >
                            {requestText}
                          </SyntaxHighlighter>
                        </div>
                      </div>
                    </div>
                  </TabsContent>
                  
                  <TabsContent value="curl" className="mt-0 w-full">
                    <div className="space-y-6">
                      <div>
                        <div className="flex justify-between items-center mb-2">
                          <h3 className="text-sm font-medium text-foreground flex items-center gap-2">
                            <Terminal size={18} />
                            cURL
                          </h3>
                          <button 
                            onClick={() => handleCopy(curlText, responseId)}
                            className="text-muted-foreground hover:text-foreground transition-colors p-1 rounded-md hover:bg-accent"
                            aria-label="Copy request"
                          >
                            {copiedStates[responseId] ? (
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
                            {curlText}
                          </SyntaxHighlighter>
                        </div>
                      </div>
                    </div>
                  </TabsContent>
                  
                  <TabsContent value="python" className="mt-0 w-full">
                    <div className="space-y-6">
                      <div>
                        <div className="flex justify-between items-center mb-2">
                          <h3 className="text-sm font-medium text-foreground flex items-center gap-2">
                            <Code size={18} />
                            Python
                          </h3>
                          <button 
                            onClick={() => handleCopy(`import requests

response = requests.post(
    "https://your-domain.com/api/flow/run",
    json={
        "flowId": "${flow.id}",
        "inputs": {}
    }
)
result = response.json()
print(result)`, "python-example")}
                            className="text-muted-foreground hover:text-foreground transition-colors p-1 rounded-md hover:bg-accent"
                            aria-label="Copy request"
                          >
                            {copiedStates["python-example"] ? (
                              <CheckIcon className="h-4 w-4 text-green-500" />
                            ) : (
                              <CopyIcon className="h-4 w-4" />
                            )}
                          </button>
                        </div>
                        <div className="rounded-md overflow-hidden">
                          <SyntaxHighlighter 
                            language="python" 
                            style={vscDarkPlus}
                            customStyle={{ margin: 0, borderRadius: '0.375rem' }}
                          >
                            {`import requests

response = requests.post(
    "https://your-domain.com/api/flow/run",
    json={
        "flowId": "${flow.id}",
        "inputs": {}
    }
)
result = response.json()
print(result)`}
                          </SyntaxHighlighter>
                        </div>
                      </div>
                    </div>
                  </TabsContent>
                </Tabs>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
