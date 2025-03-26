"use client";

import { UnifiedFlowCreator } from "../components/create/unified-flow-creator";
import { FlowChatPanel } from "../components/test/flow-test-chat";
import { useRef, useState, useEffect } from "react";
import { useChat } from 'ai/react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Settings, MessageSquare } from "lucide-react";
import { useRouter } from "next/navigation";
import { FlowHeader } from "../components/header";
import { getFlowById, updateFlowStatus } from "../api/api.flows";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";

export default function FlowCreatePage({ flowId }: { flowId?: string }) {
  const router = useRouter();
  const flowChatId = useRef(`flow-chat-${Date.now()}`).current;
  const flowCreatorRef = useRef<{ saveFlow: () => Promise<string | undefined> } | null>(null);
  const [isMobile, setIsMobile] = useState(false);
  const [flowName, setFlowName] = useState("New Flow");
  const [flow, setFlow] = useState<any>(null);
  const [isLoadingFlow, setIsLoadingFlow] = useState(!!flowId);
  const [isMounted, setIsMounted] = useState(false);
  const [isActivating, setIsActivating] = useState(false);
  
  useEffect(() => {
    setIsMounted(true);
    
    const checkScreenSize = () => {
      setIsMobile(window.innerWidth < 1024);
    };
    
    checkScreenSize();
    
    window.addEventListener('resize', checkScreenSize);
    
    return () => {
      window.removeEventListener('resize', checkScreenSize);
    };
  }, []);
  
  useEffect(() => {
    if (flowId) {
      const loadFlow = async () => {
        try {
          setIsLoadingFlow(true);
          const flowData = await getFlowById(flowId);
          if (flowData) {
            setFlow(flowData);
            setFlowName(flowData.name || "Edit Flow");
          }
        } catch (error) {
          console.error('Error loading flow:', error);
        } finally {
          setIsLoadingFlow(false);
        }
      };
      
      loadFlow();
    }
  }, [flowId]);

  const { messages, append, isLoading: isChatLoading, stop } = useChat({
    api: '/api/flow/test-from-chat',
    id: flowChatId,
    initialMessages: [],
    body: {
      flowId: flow?.id,
      chatId: flowChatId
    },
    onFinish: (message) => {
      try {
        if (message.toolInvocations && message.toolInvocations.length > 0) {
          for (const toolInvocation of message.toolInvocations) {
            if (toolInvocation.toolName === 'flow_improve_description' && toolInvocation.state === 'result') {
              try {
                const result = toolInvocation.result;
                if (result && typeof result === 'object' && result.name && result.description) {
                  return;
                }
              } catch (toolError) {
                console.error('Error processing tool result:', toolError);
              }
            }
          }
        }
        
        if (message.content) {
          try {
            const flowData = JSON.parse(message.content);
            if (flowData.name && flowData.description) {
            }
          } catch (jsonError) {
            console.log('Message is not a valid JSON, continuing...', jsonError);
          }
        }
      } catch (error) {
        console.error('Error in onFinish:', error);
      }
    }
  });

  const handleSendMessage = async (message: string) => {
    try {
      await append({
        id: `msg-${Date.now()}`,
        content: message,
        role: 'user'
      });
    } catch (error) {
      console.error('Error in handleSendMessage:', error);
    }
  };

  const handleSaveFlow = (config: { name: string; description: string; plain_description?: string; id?: string }) => {
    console.log('Сохраняем поток:', config);
    setFlowName(config.name || "New Flow");
    
    if (config.id) {
      const updatedFlow = {
        ...flow,
        id: config.id,
        name: config.name,
        description: config.description,
        plain_description: config.plain_description
      };
      setFlow(updatedFlow);
      
      if (!flowId) {
        const newUrl = `/flow/${config.id}/edit`;
        window.history.pushState(
          { ...window.history.state, as: newUrl, url: newUrl }, 
          '', 
          newUrl
        );
        console.log("URL updated without page re-render:", newUrl);
      } else {
        console.log("Update data without URL change");
      }
    }
  };

  const handleCreateFlow = () => {
    console.log('Creating new flow with name:', flowName);
    
    if (flow?.id) {
      console.log('Flow already exists, letting the header handle it');
      return;
    }
    
    router.push('/agent');
  };

  const handlePublishFlow = (publishedFlowId: string) => {
    console.log('Flow published with ID:', publishedFlowId);
    router.push('/agent');
  };

  const handleTestFlow = async () => {
    if (flow?.id) {
      console.log('Testing flow with ID:', flow.id);
      handleSendMessage("Test the provided flow.");
    } else {
      toast.error('Please save the flow first.');
      try {
        
        if (flow?.id) {
          handleSendMessage("Test the provided flow.");
        } else {
          console.error('Failed to get flow ID after saving');
        }
      } catch (error) {
        console.error('Error saving flow before test:', error);
      }
    }
  };

  const handleActivate = async () => {
    try {
      setIsActivating(true);
      
      // Save current flow state
      const savedFlowId = await flowCreatorRef.current?.saveFlow();
      if (!savedFlowId && !flow?.id) {
        toast.error("Failed to save flow");
        return;
      }
      
      const targetFlowId = savedFlowId || flow?.id;
      
      // Update flow status to Active
      await updateFlowStatus(targetFlowId, "Active");
      handlePublishFlow(targetFlowId);
      router.push(`/flow/${targetFlowId}/view`);
    } catch (error) {
      console.error("Error activating flow:", error);
      toast.error("Failed to activate flow");
    } finally {
      setIsActivating(false);
    }
  };

  if (!isMounted || isLoadingFlow) {
    return (
      <div className="h-screen overflow-hidden flex flex-col">
        <div className="flex items-center justify-between w-full px-4 py-2 bg-white border-b border-gray-200">
          <div className="flex items-center gap-2">
            <Skeleton className="w-6 h-6 rounded-full" />
            <Skeleton className="w-40 h-5" />
          </div>
          <Skeleton className="w-20 h-7 rounded-full" />
        </div>
        
        <div className="flex flex-1 overflow-hidden">
          <div className="w-[700px] border-r border-border bg-muted/10 flex flex-col h-full overflow-hidden p-6">
            <div className="flex flex-col h-full gap-6">
              <Skeleton className="w-36 h-8 mb-4" />
              <Skeleton className="w-full h-10 mb-2" />
              <Skeleton className="w-full h-[200px] mb-4" />
              <Skeleton className="w-full h-10 mb-2" />
              <Skeleton className="w-full h-[100px]" />
            </div>
          </div>

          <div className="flex-1 h-full overflow-hidden">
            <div className="h-full flex items-center justify-center">
              <Skeleton className="w-[400px] h-[300px]" />
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (isMobile) {
    return (
      <div className="h-screen overflow-hidden flex flex-col">
        <FlowHeader 
          flowName={flowName} 
          onBack={() => router.back()}
          onCreateClick={handleCreateFlow}
          onPublish={handlePublishFlow}
          isLoading={isLoadingFlow}
          flowId={flow?.id}
          onActivate={handleActivate}
          isActivating={isActivating}
        />
        <Tabs defaultValue="chat" className="w-full h-full flex flex-col">
          <TabsList className="grid grid-cols-2 mb-2">
            <TabsTrigger value="chat" className="flex items-center gap-2">
              <MessageSquare className="h-4 w-4" />
              <span>Chat</span>
            </TabsTrigger>
            <TabsTrigger value="editor" className="flex items-center gap-2">
              <Settings className="h-4 w-4" />
              <span>Editor</span>
            </TabsTrigger>
          </TabsList>
          
          <TabsContent value="chat" className="flex-1 overflow-hidden m-0 h-full">
            <FlowChatPanel
              messages={messages}
              isLoading={isChatLoading}
              chatId={flowChatId}
              onSubmit={handleSendMessage}
              onStop={stop}
            />
          </TabsContent>
          
          <TabsContent value="editor" className="flex-1 overflow-hidden m-0 h-full">
            <UnifiedFlowCreator 
              onSave={handleSaveFlow}
              onTest={handleTestFlow}
              chatMessages={messages}
              flowChatId={flowChatId}
              initialData={flow ? {
                id: flow.id,
                name: flow.name,
                description: flow.description
              } : undefined}
              isLoading={isLoadingFlow}
              isTestRunning={isChatLoading}
              creatorRef={flowCreatorRef}
            />
          </TabsContent>
        </Tabs>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen overflow-hidden">
      <FlowHeader 
        flowName={flowName} 
        onBack={() => router.back()}
        onCreateClick={handleCreateFlow}
        onPublish={handlePublishFlow}
        isLoading={isLoadingFlow}
        flowId={flow?.id}
        onActivate={handleActivate}
        isActivating={isActivating}
      />
      <div className="flex flex-1 overflow-hidden">
        <div className="w-[700px] border-r border-border bg-muted/10 flex flex-col h-full overflow-hidden">
          <UnifiedFlowCreator 
            onSave={handleSaveFlow}
            onTest={handleTestFlow}
            chatMessages={messages}
            flowChatId={flowChatId}
            initialData={flow ? {
              id: flow.id,
              name: flow.name,
              description: flow.description
            } : undefined}
            isLoading={isLoadingFlow}
            isTestRunning={isChatLoading}
            creatorRef={flowCreatorRef}
          />
        </div>

        <div className="flex-1 h-full overflow-hidden">
          <FlowChatPanel
            messages={messages}
            isLoading={isChatLoading}
            chatId={flowChatId}
            onSubmit={handleSendMessage}
            onStop={stop}
          />
        </div>
      </div>
    </div>
  );
}