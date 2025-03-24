"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useState, useEffect, useRef } from "react";
import ContentEditable from "react-contenteditable";
import { ActionItem } from "@/app/modules/flows/components/action-item";
import { Wand2, Loader2, MessageSquare, Settings } from "lucide-react";
import { useCompletion } from 'ai/react';
import { useActionsMention } from "./use-action-mention";
import { useToolsDetector, ToolsList } from "../flow-description-tool-detector";
import { extractTextFromHTML, isEmptyHTML } from "../flow-description-html";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ChatFlowCreator } from "./chat-flow-creator";

interface FlowConfigurationProps {
  onSave?: (config: { name: string; description: string }) => void;
  onTest?: () => void;
  actions: any[];
}

export function FlowConfiguration({ onSave, onTest, actions }: FlowConfigurationProps) {
  const [name, setName] = useState("");
  const [html, setHtml] = useState("");
  const contentEditableRef = useRef<any>(null);
  const lastHtml = useRef("");
  const [activeTab, setActiveTab] = useState<string>("configure");

  const { complete, completion, isLoading: isImproving } = useCompletion({
    api: '/api/flow/improve-description',
    onFinish: (completion) => {
      if (completion) {
        setHtml(completion);
      }
    }
  });

  const { usedTools } = useToolsDetector(html, actions);
  
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

  const handleSave = () => {
    const plainText = extractTextFromHTML(html);
    
    onSave?.({ 
      name, 
      description: plainText 
    });
  };

  const handleAIImprove = async () => {
    if (!html || isImproving) return;
    
    const plainText = extractTextFromHTML(html);
    
    if (plainText.trim().length === 0) return;
    
    try {
      setHtml('');
      await complete('', { 
        body: { description: plainText }
      });
    } catch (error) {
      console.error('Error improving description:', error);
    }
  };

  const handleActionsListKeyDown = (e: React.KeyboardEvent<HTMLDivElement>) => {
    if (['ArrowDown', 'ArrowUp', 'Enter', 'Escape'].includes(e.key)) {
      e.stopPropagation();
    }
  };

  return (
    <div className="flex flex-col h-full gap-6 p-6">
      <h2 className="text-2xl font-semibold">Flow Configuration</h2>
      
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full flex-1 flex flex-col">
        <TabsList className="grid grid-cols-2 mb-4">
          <TabsTrigger value="create" className="flex items-center gap-2">
            <MessageSquare className="h-4 w-4" />
            <span>Chat Create</span>
          </TabsTrigger>
          <TabsTrigger value="configure" className="flex items-center gap-2">
            <Settings className="h-4 w-4" />
            <span>Configure</span>
          </TabsTrigger>
        </TabsList>
        
        <TabsContent value="create" className="flex-1 h-full">
          <div className="h-full">
            <ChatFlowCreator 
              actions={actions} 
              onFlowGenerated={(generatedFlow) => {
                setName(generatedFlow.name);
                setHtml(generatedFlow.description);
                setActiveTab("configure");
              }} 
            />
          </div>
        </TabsContent>
        
        <TabsContent value="configure">
          <div className="space-y-4 overflow-y-auto max-h-[calc(100vh-250px)]">
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
                    className="editor-content min-h-[600px] h-[600px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 block"
                    data-placeholder="Describe the flow you would like to create... Use @ to mention actions"
                  />
                ) : (
                  <div className="editor-content min-h-[600px] h-[600px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm relative">
                    <div dangerouslySetInnerHTML={{ __html: completion || '' }} />
                  </div>
                )}
                
                <button 
                  className="absolute bottom-3 right-3 inline-flex items-center justify-center h-7 w-7 text-foreground bg-white border border-input hover:bg-muted rounded-md transition-colors shadow-sm"
                  onClick={handleAIImprove}
                  title="Improve with AI"
                  disabled={isImproving}
                >
                  {isImproving ? 
                    <Loader2 className="h-4 w-4 animate-spin" /> : 
                    <Wand2 className="h-4 w-4" />
                  }
                </button>
                
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

          <div className="flex gap-3 mt-6">
            <Button variant="outline" onClick={onTest} className="flex-1">
              Test
            </Button>
            <Button onClick={handleSave} className="flex-1">
              Save
            </Button>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}