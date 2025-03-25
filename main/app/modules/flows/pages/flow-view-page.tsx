"use client";

import { useEffect, useState } from "react";
import { getFlowById, getUserActions, getPublicFlowById, getFlowActions, getPublicFlowActions, getActionsByIds } from "../api/api.flows";
import { useRouter } from "next/navigation";
import { FlowHeader } from "../components/header";
import { ToolsList } from "../components/flow-description-tool-detector";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { Code, Copy, Edit, Terminal, Info, Play, CheckIcon, CopyIcon, ExternalLink } from "lucide-react";
import { toast } from "sonner";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { isEmptyHTML } from "../components/flow-description-html";
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { createClient } from '@/lib/utils/supabase/client';
import { getProviderActionsForFlow } from "../api/api.flows";

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
  isPublic?: boolean;
}

function QuickStart({ flowName = "", isOwner = false, isAuthenticated = false }: { 
  flowName?: string;
  isOwner?: boolean;
  isAuthenticated?: boolean;
}) {
  const [copied, setCopied] = useState(false);
  const commandText = `Run «${flowName}» flow via VeyraX.`;

  return (
    <div className="bg-white rounded-md border p-6 space-y-4">
      <h2 className="text-xl font-medium text-foreground">Quick Start</h2>
      <div className="text-sm text-muted-foreground space-y-3">
        <p>
          This flow is designed to run by AI agents. You can execute it through any system 
          where these AI agents can make calls to Veyrax using our <a href="https://docs.veyrax.com/api" 
          className="text-gray-900 inline-flex items-center gap-1 hover:underline">
            API toolkit
            <ExternalLink className="h-2.5 w-2.5" />
          </a>.
        </p>
        <p>
          Common ways to run this flow via <a href="https://cursor.sh" 
          className="text-gray-900 inline-flex items-center gap-1 hover:underline">
            Cursor / Windsurf / Cline / Claude
            <ExternalLink className="h-2.5 w-2.5" />
          </a> or any other MCP compatible environment.
        </p>
        {(!isAuthenticated || !isOwner) && (
          <p className="text-muted-foreground">
            To clone this flow and implement it in your own environment, simply click the Clone button in the header. 
            Before using the cloned flow, make sure you have all the required tools enabled in your account.
          </p>
        )}
        <p>
          To get it running, just ask Agent to run the flow:
        </p>
        <div className="relative">
          <div className="absolute right-3 top-1/2 -translate-y-1/2">
            <button
              onClick={() => {
                navigator.clipboard.writeText(commandText);
                setCopied(true);
                setTimeout(() => setCopied(false), 2000);
              }}
              className="h-6 w-6 p-0 flex items-center justify-center"
            >
              {copied ? <CheckIcon className="h-4 w-4" /> : <CopyIcon className="h-4 w-4" />}
            </button>
          </div>
          <SyntaxHighlighter
            language="bash"
            style={vscDarkPlus}
            customStyle={{ margin: 0, borderRadius: '0.375rem', paddingRight: '2.5rem' }}
          >
            {commandText}
          </SyntaxHighlighter>
        </div>
      </div>
    </div>
  );
}

export default function FlowViewPage({ flowId, isPublic = false }: FlowViewPageProps) {
  const router = useRouter();
  const [flow, setFlow] = useState<any>(null);
  const [actions, setActions] = useState<any[]>([]);
  const [isOwner, setIsOwner] = useState(false);
  const [isLoadingFlow, setIsLoadingFlow] = useState(true);
  const [usedTools, setUsedTools] = useState<any[]>([]);
  const [copiedStates, setCopiedStates] = useState<Record<string, boolean>>({});
  const [flowActions, setFlowActions] = useState<string[]>([]);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  
  useEffect(() => {
    const checkAuth = async () => {
      const supabase = createClient();
      const { data: { user } } = await supabase.auth.getUser();
      setIsAuthenticated(!!user);
    };
    
    checkAuth();
  }, []);
  
  useEffect(() => {
    const loadFlow = async () => {
      try {
        setIsLoadingFlow(true);
        
        if (isPublic) {
          const publicFlowData = await getPublicFlowById(flowId);
          if (publicFlowData) {
            setFlow(publicFlowData);
            setIsOwner(false);
            
            try {
              const flowActionsData = await getPublicFlowActions(flowId);
              setFlowActions(flowActionsData);
              
              if (flowActionsData.length > 0) {
                const actionsData = await getActionsByIds(flowActionsData);
                setActions(actionsData);
              } else {
                setActions([]);
              }
            } catch (actionsError) {
              console.error('Error loading actions for public flow:', actionsError);
              setFlowActions([]);
              setActions([]);
            }
          } else {
            setFlow(null);
          }
        } else {
          try {
            const flowData = await getFlowById(flowId);
            if (flowData) {
              setFlow(flowData);
              setIsOwner(true);
              
              const actionsData = await getUserActions();
              setActions(actionsData);
              
              const flowActionsData = await getFlowActions(flowId);
              setFlowActions(flowActionsData);
            }
          } catch (error) {
            console.error('Error fetching flow by ID:', error);
            setFlow(null);
          }
        }
      } catch (error) {
        console.error('Error loading flow:', error);
        setFlow(null);
      } finally {
        setIsLoadingFlow(false);
      }
    };
    
    if (flowId) {
      loadFlow();
    }
  }, [flowId, isPublic]);
  
  useEffect(() => {
    if (flow && actions.length > 0 && flowActions.length > 0) {
      const toolsMap = new Map();
      
      const relevantActions = isPublic 
        ? actions 
        : actions.filter(action => flowActions.includes(action.action_id));
      
      relevantActions.forEach(action => {
        if (!toolsMap.has(action.provider_id)) {
          toolsMap.set(action.provider_id, {
            provider_id: action.provider_id,
            provider_name: action.provider_name,
            logo_url: action.logo_url
          });
        }
      });
      
      setUsedTools(Array.from(toolsMap.values()));
    } else if (flow && flow.description && actions.length > 0) {
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
  }, [flow, actions, flowActions, isPublic]);
  
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
  
  const getShareableUrl = () => {
    if (typeof window === 'undefined') return '';
    return `${window.location.origin}/flow/${flowId}/shared`;
  };
  
  const handleCopyLink = () => {
    const url = getShareableUrl();
    navigator.clipboard.writeText(url);
    toast.success("Link copied");
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
            
            <div className="flex flex-col space-y-6">
              <div className="bg-white rounded-md border p-6 space-y-4">
                <Skeleton className="w-32 h-6" />
                <div className="space-y-3">
                  <Skeleton className="w-full h-16" />
                  <Skeleton className="w-full h-16" />
                  <Skeleton className="w-full h-16" />
                  <Skeleton className="w-full h-8" />
                  <div className="relative mt-2">
                    <Skeleton className="w-full h-12 rounded-md" />
                    <div className="absolute right-3 top-1/2 -translate-y-1/2">
                      <Skeleton className="w-6 h-6 rounded-md" />
                    </div>
                  </div>
                </div>
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
  
  const getFlowsExample = `curl -X GET "https://veyaraxapp.com/api/flows" \\
-H "Content-Type: application/json" \\
-H "Authorization: VEYRAX_API_KEY"`;

  const getFlowExample = `curl -X GET "https://veyaraxapp.com/api/flows/${flowId}" \\
-H "Content-Type: application/json" \\
-H "Authorization: VEYRAX_API_KEY"`;
  
  return (
    <div className="flex flex-col h-screen overflow-hidden">
      <FlowHeader 
        flowName={flow?.name || "Flow"} 
        onBack={handleBack}
        isLoading={isLoadingFlow}
        flowId={flow?.id}
        isOwner={isOwner}
        isAuthenticated={isAuthenticated}
        isShared={flow?.is_shared || false}
      />
      
      <div className="flex-1 overflow-auto">
        <div className="w-full px-6 py-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="space-y-6">
              <div className="bg-white rounded-md border p-6 space-y-4">
                <h2 className="text-xl font-medium text-foreground">Overview</h2>
                
                {flow.description && !isEmptyHTML(flow.description) ? (
                  <div className="prose prose-sm md:prose-base max-w-none text-foreground prose-headings:font-semibold prose-h1:text-2xl prose-h2:text-xl prose-h3:text-lg prose-p:text-foreground/90 prose-ul:list-disc prose-ol:list-decimal prose-ul:pl-5 prose-ol:pl-5 prose-li:my-3">
                    <div dangerouslySetInnerHTML={{ __html: cleanHtml(flow.description) }} />
                  </div>
                ) : (
                  <div className="text-muted-foreground">
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
            
            <div className="flex flex-col space-y-6">
              <QuickStart 
                flowName={flow?.name} 
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
          </div>
        </div>
      </div>
    </div>
  );
}
