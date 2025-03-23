"use client";

import { useChat } from 'ai/react';
import { useRef, useState, useEffect } from 'react';
import { ChatMessages } from "@/app/modules/agent/components/messages/chat-messages";
import { AIInputWithSearch } from "@/app/modules/agent/components/input/ai-input";
import { FlowChatCreateEmptyState } from "./flow-chat-create-empty-state";
import { type Message } from 'ai/react';

interface ChatFlowCreatorProps {
  actions: any[];
  onFlowGenerated: (flowData: { name: string; description: string }) => void;
  externalMessages?: Message[];
  externalChatId?: string;
  externalIsLoading?: boolean;
  externalOnSubmit?: (message: string) => Promise<void>;
  externalOnStop?: () => void;
  useExternalChat?: boolean;
}

export function ChatFlowCreator({ 
  actions, 
  onFlowGenerated,
  externalMessages,
  externalChatId,
  externalIsLoading,
  externalOnSubmit,
  externalOnStop,
  useExternalChat = false
}: ChatFlowCreatorProps) {
  const temporaryFlowChatId = useRef(`flow-chat-${Date.now()}`).current;
  const [hasSubmitted, setHasSubmitted] = useState(false);

  const { messages: localMessages, append, isLoading: localIsLoading, stop: localStop, setMessages } = useChat({
    api: '/api/flow/create-from-chat',
    id: useExternalChat && externalChatId ? externalChatId : temporaryFlowChatId,
    initialMessages: [],
    onFinish: (message) => {
      try {
        if (message.toolInvocations && message.toolInvocations.length > 0) {
          for (const toolInvocation of message.toolInvocations) {
            if (toolInvocation.toolName === 'flow_improve_description' && toolInvocation.state === 'result') {
              try {
                const result = toolInvocation.result;
                if (result && typeof result === 'object' && result.name && result.description) {
                  onFlowGenerated(result);
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
              onFlowGenerated(flowData);
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

  const messages = useExternalChat && externalMessages ? externalMessages : localMessages;
  const isLoading = useExternalChat && externalIsLoading !== undefined ? externalIsLoading : localIsLoading;
  const chatId = useExternalChat && externalChatId ? externalChatId : temporaryFlowChatId;
  const hasMessages = messages.length > 0;
  
  const handleSendMessage = async (value: string) => {
    try {
      setHasSubmitted(true);
      
      if (useExternalChat && externalOnSubmit) {
        await externalOnSubmit(value);
      } else {
        const messageId = `msg-${Date.now()}`;
        await append({
          id: messageId,
          content: value,
          role: 'user'
        });
      }
    } catch (error) {
      console.error('Error in handleSendMessage:', error);
    }
  };

  const handleStop = () => {
    if (useExternalChat && externalOnStop) {
      externalOnStop();
    } else {
      localStop();
    }
  };

  const messagesContainerRef = useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    if (messagesContainerRef.current) {
      messagesContainerRef.current.scrollTop = messagesContainerRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div className="flex flex-col h-full relative">
      <div className="absolute inset-0 flex flex-col overflow-hidden">
        <div 
          ref={messagesContainerRef} 
          className="flex-1 overflow-y-auto scrollbar-thin relative"
          style={{ paddingBottom: "90px" }}
        >
          {hasMessages ? (
            <ChatMessages 
              chatId={chatId}
              messages={messages as Message[]}
              isLoading={isLoading}
              onSendMessage={handleSendMessage}
              isFlow={false}
            />
          ) : (
            <FlowChatCreateEmptyState />
          )}
        </div>
        
        <div className="absolute bottom-0 left-0 right-0 px-4 pt-2 bg-background">
          <AIInputWithSearch
            placeholder="Describe the flow you want to create..."
            onSubmit={handleSendMessage}
            className="max-w-none"
            isLoading={isLoading}
            onStop={handleStop}
            userTools={{}}
          />
        </div>
      </div>
    </div>
  );
} 