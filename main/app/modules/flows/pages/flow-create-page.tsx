"use client";

import { UnifiedFlowCreator } from "../components/create/unified-flow-creator";
import { FlowChatPanel } from "../components/test/flow-test-chat";
import { useRef, useState, useEffect } from "react";
import { useChat } from 'ai/react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Settings, MessageSquare } from "lucide-react";

export default function FlowCreatePage() {
  // Создаем постоянный ID для чата
  const flowChatId = useRef(`flow-chat-${Date.now()}`).current;
  const [isMobile, setIsMobile] = useState(false);

  // Отслеживание размера экрана
  useEffect(() => {
    const checkScreenSize = () => {
      setIsMobile(window.innerWidth < 1024);
    };
    
    // Проверка при загрузке
    checkScreenSize();
    
    // Слушатель изменения размера окна
    window.addEventListener('resize', checkScreenSize);
    
    return () => {
      window.removeEventListener('resize', checkScreenSize);
    };
  }, []);

  // Используем useChat для управления чатом на глобальном уровне
  const { messages, append, isLoading: isChatLoading, stop } = useChat({
    api: '/api/flow/create-from-chat',
    id: flowChatId,
    initialMessages: [],
    onFinish: (message) => {
      try {
        // Обработка завершения сообщения остается прежней
        if (message.toolInvocations && message.toolInvocations.length > 0) {
          for (const toolInvocation of message.toolInvocations) {
            if (toolInvocation.toolName === 'flow_improve_description' && toolInvocation.state === 'result') {
              try {
                const result = toolInvocation.result;
                if (result && typeof result === 'object' && result.name && result.description) {
                  // Данные можно передать в UnifiedFlowCreator через колбэк
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
              // Здесь также можно обработать данные
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

  const handleSaveFlow = (config: { name: string; description: string }) => {
    console.log('Saving flow:', config);
  };

  const handleTestFlow = () => {
    console.log('Testing flow');
  };

  if (isMobile) {
    return (
      <div className="h-screen overflow-hidden flex flex-col">
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
            />
          </TabsContent>
        </Tabs>
      </div>
    );
  }

  return (
    <div className="flex h-screen overflow-hidden">
      <div className="w-[700px] border-r border-border bg-muted/10 flex flex-col h-full overflow-hidden">
        <UnifiedFlowCreator 
          onSave={handleSaveFlow}
          onTest={handleTestFlow}
          chatMessages={messages}
          flowChatId={flowChatId}
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
  );
}