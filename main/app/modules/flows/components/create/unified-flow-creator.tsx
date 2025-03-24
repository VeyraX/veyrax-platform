"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useState, useEffect, useRef } from "react";
import { getUserActions } from "@/app/modules/flows/api/api.flows";
import ContentEditable from "react-contenteditable";
import { ActionItem } from "@/app/modules/flows/components/action-item";
import { Loader2 } from "lucide-react";
import { useChat } from 'ai/react';
import { useActionsMention } from "./use-action-mention";
import { useToolsDetector, ToolsList } from "../flow-description-tool-detector";
import { extractTextFromHTML, isEmptyHTML } from "../flow-description-html";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { type Message } from 'ai/react';
import { ChatFlowCreator } from "./chat-flow-creator";
import { updateFlowWithExtractedActions, saveFlowWithExtractedActions } from "@/app/modules/flows/api/api.flows";
import { Skeleton } from "@/components/ui/skeleton";

interface UnifiedFlowCreatorProps {
  onSave?: (config: { name: string; description: string; plain_description?: string; id?: string }) => void;
  onTest?: () => void;
  chatMessages?: Message[];
  flowChatId?: string;
  initialData?: {
    id: string;
    name: string;
    description: string;
    plain_description?: string;
  };
  isLoading?: boolean;
}

export function UnifiedFlowCreator({ 
  onSave, 
  onTest, 
  chatMessages, 
  flowChatId, 
  initialData,
  isLoading = false
}: UnifiedFlowCreatorProps) {
  const [activeTab, setActiveTab] = useState<string>(initialData ? "configure" : "create");
  
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const storedTab = localStorage.getItem('flowCreatorActiveTab');
      if (storedTab) {
        setActiveTab(storedTab);
      }
    }
  }, []);
  
  const [name, setName] = useState(initialData?.name || "");
  const [html, setHtml] = useState(initialData?.description || "");
  const [actions, setActions] = useState<any[]>([]);
  const [isActionsLoading, setIsActionsLoading] = useState(true);
  const [isImproving, setIsImproving] = useState(false);
  const [flowId, setFlowId] = useState<string | undefined>(initialData?.id);
  const [isSaving, setIsSaving] = useState(false);
  
  const contentEditableRef = useRef<any>(null);
  const lastHtml = useRef("");
  
  const flowCreatorChatId = useRef(`flow-creator-${Date.now()}`).current;

  // Handle tab changes
  const handleTabChange = (value: string) => {
    setActiveTab(value);
    if (typeof window !== 'undefined') {
      localStorage.setItem('flowCreatorActiveTab', value);
    }
  };
  
  const { messages, append, isLoading: isChatLoading, stop } = useChat({
    api: '/api/flow/create-from-chat',
    id: flowCreatorChatId,
    initialMessages: [],
    onFinish: (message) => {
      try {
        if (message.toolInvocations && message.toolInvocations.length > 0) {
          for (const toolInvocation of message.toolInvocations) {
            if (toolInvocation.toolName === 'flow_improve_description' && toolInvocation.state === 'result') {
              try {
                const result = toolInvocation.result;
                if (result && typeof result === 'object' && result.name && result.description) {
                  setName(result.name);
                  setHtml(result.description);
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
              setName(flowData.name);
              setHtml(flowData.description);
              setActiveTab("configure");
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

  const handleSendCreatorMessage = async (value: string) => {
    try {
      await append({
        id: `msg-${Date.now()}`,
        content: value,
        role: 'user'
      });
    } catch (error) {
      console.error('Error in handleSendCreatorMessage:', error);
    }
  };

  useEffect(() => {
    const loadActions = async () => {
      setIsActionsLoading(true);
      try {
        const fetchedActions = await getUserActions();
        console.log(fetchedActions);
        setActions(fetchedActions);
      } catch (error) {
        console.error('Error loading actions:', error);
      } finally {
        setIsActionsLoading(false);
      }
    };

    loadActions();
  }, []);

  useEffect(() => {
    if (initialData) {
      setName(initialData.name || "");
      setHtml(initialData.description || "");
      setFlowId(initialData.id);
    }
  }, [initialData]);

  const { 
    filteredActions, 
    showActions, 
    setShowActions,
    searchQuery,
    setSearchQuery,
    cursorPosition,
    setCursorPosition,
    selectedActionIndex,
    actionsListRef,
    handleActionSelect,
    processEditorChange
  } = useActionsMention(contentEditableRef, actions);

  const { usedTools } = useToolsDetector(html, actions);

  const handleChange = (evt: any) => {
    const newHtml = evt.target.value;
    
    if (isEmptyHTML(newHtml)) {
      setHtml('');
    } else {
      setHtml(newHtml);
    }
    
    const { showActions: newShowActions, searchQuery: newSearchQuery, cursorPosition: newCursorPosition } = 
      processEditorChange(newHtml, evt);
    
    setShowActions(newShowActions);
    if (newSearchQuery !== undefined) setSearchQuery(newSearchQuery);
    if (newCursorPosition !== null) setCursorPosition(newCursorPosition);
    
    lastHtml.current = newHtml;
  };

  const handleSave = async () => {
    try {
      setIsSaving(true);
      
      const plainText = extractTextFromHTML(html);
      let currentFlowId = flowId;
      
      if (!currentFlowId) {
        currentFlowId = await saveFlowWithExtractedActions({
          name,
          html
        }, actions);
        
        setFlowId(currentFlowId);
      } else {
        await updateFlowWithExtractedActions(currentFlowId, {
          name,
          html
        }, actions);
      }
      
      onSave?.({ 
        name, 
        description: html,
        plain_description: plainText,
        id: currentFlowId
      });
    } catch (error) {
      console.error('Error saving flow:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const handleAIImprove = async () => {
    if (!html || isImproving) return;
    
    const plainText = extractTextFromHTML(html);
    
    if (plainText.trim().length === 0) return;
    
    try {
      setIsImproving(true);
      
      const response = await fetch('/api/flow/improve-description', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
          description: plainText,
          name: name 
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to improve description');
      }
      
      const result = await response.json();
      
      if (result.name) {
        setName(result.name);
      }
      
      if (result.description) {
        setHtml(result.description);
      }
      
    } catch (error) {
      console.error('Error improving description:', error);
    } finally {
      setIsImproving(false);
    }
  };

  const handleActionsListKeyDown = (e: React.KeyboardEvent<HTMLDivElement>) => {
    if (['ArrowDown', 'ArrowUp', 'Enter', 'Escape'].includes(e.key)) {
      e.stopPropagation();
    }
  };

  if (isLoading) {
    return (
      <div className="flex flex-col h-full gap-6 p-6">
        <Skeleton className="w-36 h-8 mb-4" />
        <div className="space-y-4 flex-grow">
          <div className="space-y-2">
            <Skeleton className="w-24 h-5" />
            <Skeleton className="w-full h-10" />
          </div>
          <div className="space-y-2">
            <Skeleton className="w-24 h-5" />
            <Skeleton className="w-full h-[200px]" />
          </div>
          <div className="space-y-2">
            <Skeleton className="w-24 h-5" />
            <Skeleton className="w-full h-[50px]" />
          </div>
        </div>
        <div className="flex gap-3 mt-4">
          <Skeleton className="w-full h-10" />
          <Skeleton className="w-full h-10" />
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full gap-6 p-6">
      <Tabs value={activeTab} onValueChange={handleTabChange} className="w-full flex-1 flex flex-col">
        <TabsList className="h-auto gap-4 rounded-none bg-transparent px-0 py-1 text-foreground mb-4">
          <TabsTrigger 
            className="relative after:absolute after:inset-x-0 after:bottom-0 after:-mb-1 after:h-0.5 hover:bg-accent hover:text-foreground data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:after:bg-primary data-[state=active]:hover:bg-accent" 
            value="create"
          >
            Create Flow
          </TabsTrigger>
          <TabsTrigger 
            className="relative after:absolute after:inset-x-0 after:bottom-0 after:-mb-1 after:h-0.5 hover:bg-accent hover:text-foreground data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:after:bg-primary data-[state=active]:hover:bg-accent" 
            value="configure"
          >
            Configure Flow
          </TabsTrigger>
        </TabsList>
        
        <TabsContent value="create" className="flex-1 h-full">
          <div className="h-full flex flex-col overflow-hidden">
            <ChatFlowCreator 
              actions={actions} 
              onFlowGenerated={(flowData) => {
                setName(flowData.name);
                setHtml(flowData.description);
                setActiveTab("configure");
              }}
              useExternalChat={true}
              externalMessages={messages}
              externalChatId={flowCreatorChatId}
              externalIsLoading={isChatLoading}
              externalOnSubmit={handleSendCreatorMessage}
              externalOnStop={stop}
            />
          </div>
        </TabsContent>
        
        <TabsContent value="configure" className="mt-0 flex-1 overflow-auto">
          <div className="flex flex-col h-full">
            <div className="space-y-4 flex-grow">
              <div className="space-y-2">
                <label className="text-sm font-medium">Flow Name</label>
                <Input
                  placeholder="Enter flow name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Description</label>
                <div className="relative">
                  {!isImproving ? (
                    <ContentEditable
                      innerRef={contentEditableRef}
                      html={html}
                      onChange={handleChange}
                      className="editor-content min-h-[100px] h-auto w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 block"
                      data-placeholder="Describe the flow you would like to create... Use @ to mention actions"
                    />
                  ) : (
                    <div className="editor-content min-h-[100px] h-auto w-full rounded-md border border-input bg-background px-3 py-2 text-sm relative flex items-center justify-center">
                      <Loader2 className="h-6 w-6 animate-spin" />
                    </div>
                  )}
                  
                  {showActions && cursorPosition && (
                    <div 
                      ref={actionsListRef}
                      className="absolute z-50 w-64 bg-background border rounded-lg shadow-lg max-h-[300px] overflow-y-auto"
                      style={{
                        top: `${cursorPosition.top}px`,
                        left: `${cursorPosition.left}px`,
                      }}
                      onKeyDown={handleActionsListKeyDown}
                      tabIndex={-1}
                    >
                      {filteredActions.length > 0 ? (
                        filteredActions.map((action, index) => (
                          <button 
                            key={action.action_id || `${action.provider_id}-${action.action_name}-${index}`}
                            data-index={index}
                            className={`w-full text-left ${index === selectedActionIndex ? 'bg-primary/10' : ''} cursor-pointer`}
                            onClick={(e) => {
                              e.preventDefault();
                              e.stopPropagation();
                              const newHtml = handleActionSelect(action);
                              if (newHtml) setHtml(newHtml);
                            }}
                          >
                            <ActionItem
                              actionName={action.action_name}
                              logoUrl={action.logo_url}
                              providerName={action.provider_name}
                            />
                          </button>
                        ))
                      ) : (
                        <div className="p-2 text-sm text-muted-foreground">No actions found</div>
                      )}
                    </div>
                  )}
                </div>
              </div>
              
              <div className="space-y-2">
                <label className="text-sm font-medium">Tools</label>
                <ToolsList tools={usedTools} />
              </div>
            </div>

            <div className="w-full bg-background pt-2 px-6 mt-auto">
              <div className="flex gap-3 mt-2">
                <Button variant="outline" onClick={onTest} className="flex-1">
                  Test
                </Button>
                <Button onClick={handleSave} className="flex-1" disabled={isSaving}>
                  {isSaving ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin mr-2" />
                      Saving...
                    </>
                  ) : (
                    "Save"
                  )}
                </Button>
              </div>
            </div>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
} 