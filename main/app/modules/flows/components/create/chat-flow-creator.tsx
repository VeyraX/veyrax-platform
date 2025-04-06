"use client";

import { useChat } from 'ai/react';
import { useRef, useState, useEffect } from 'react';
import { ChatMessages } from "@/app/modules/agent/components/messages/chat-messages";
import { AIInputWithSearch } from "@/app/modules/agent/components/input/ai-input";
import { FlowChatCreateEmptyState } from "./flow-chat-create-empty-state";
import { type Message } from 'ai/react';
import { ProviderAction } from '../../api/types.flows';

interface ChatFlowCreatorProps {
  actions: any[];
  userTools: ProviderAction[];
  onFlowGenerated: (flowData: { name: string; description: string }) => void;
  useExternalChat?: boolean;
  externalMessages?: Message[];
  externalChatId?: string;
  externalIsLoading?: boolean;
  externalOnSubmit?: (value: string) => Promise<void>;
  externalOnStop?: () => void;
  flowId?: string;
}

export function ChatFlowCreator({ 
  actions, 
  userTools,
  onFlowGenerated,
  useExternalChat = false,
  externalMessages,
  externalChatId,
  externalIsLoading,
  externalOnSubmit,
  externalOnStop,
  flowId
}: ChatFlowCreatorProps) {
  const temporaryFlowChatId = useRef(`flow-chat-${Date.now()}`).current;
  const [hasSubmitted, setHasSubmitted] = useState(false);
  const [inputValue, setInputValue] = useState("");

  const { messages: localMessages, append, isLoading: localIsLoading, stop: localStop, setMessages } = useChat({
    api: '/api/flow/create-from-chat',
    id: useExternalChat && externalChatId ? externalChatId : temporaryFlowChatId,
    body: {
      flowId: flowId,
      chatId: useExternalChat && externalChatId ? externalChatId : temporaryFlowChatId
    },
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

  useEffect(() => {
    const handleInputValueChange = (e: any) => {
      if (e.detail && e.detail.value) {
        setInputValue(e.detail.value);
      }
    };

    window.addEventListener('inputValueChange', handleInputValueChange);
    return () => {
      window.removeEventListener('inputValueChange', handleInputValueChange);
    };
  }, []);

  const handleInputSubmit = (value: string) => {
    setInputValue("");
    handleSendMessage(value);
  };

  const handleInputChange = (value: string) => {
    setInputValue(value);
  };

  return (
    <div className="flex flex-col h-full relative">
      <div className="absolute inset-0 flex flex-col">
        <div className="flex-1 overflow-y-auto [&::-webkit-scrollbar]:hidden [-ms-overflow-style:none] [scrollbar-width:none]">
          {hasMessages ? (
            <div className="pb-[120px]">
              <ChatMessages 
                chatId={chatId}
                messages={messages as Message[]}
                isLoading={isLoading}
                onSendMessage={handleSendMessage}
                isFlow={false}
                hideRatings={true}
              />
            </div>
          ) : (
            <FlowChatCreateEmptyState 
              onSendMessage={handleSendMessage}
              userTools={userTools}
            />
          )}
        </div>
        
        <div className="sticky bottom-0 px-4 pt-2 bg-background">
          <AIInputWithSearch
            placeholder="Describe the flow you want to create..."
            onSubmit={handleInputSubmit}
            onChange={handleInputChange}
            value={inputValue}
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