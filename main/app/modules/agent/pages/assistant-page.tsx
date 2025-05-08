"use client"
import React, { useState, useEffect, useRef } from "react"
import { ScrollArea } from "@/components/ui/scroll-area"
import { useChat } from 'ai/react'
import { AIInputWithSearch } from "../components/input/ai-input"
import { Header } from "../../general/components/header"
import { ChatMessages } from "../components/messages/chat-messages"
import { type Message } from 'ai/react'
import { AssistantEmptyState } from "./assistant-empty-state";
import { createChat } from "../api/api.agent";
import { useRouter, useSearchParams } from "next/navigation";
import { createChatMessage } from "../api/api.agent";
import { getChatMessages } from "../api/api.agent";
import { Loader2, AlertCircle } from "lucide-react"
import { getChat } from "../api/api.agent";
import { getUserToolsClient } from "@/lib/utils/get-user-tools-client";
import { getUserConnectedTools } from "@/app/modules/integrations/api/api.integrations";
import { updateChatTitle } from "../api/api.agent";
import { getAvailableModels } from "../api/api.agent";
import { getUserPlaygroundSettings, saveUserPlaygroundSettings } from "../../settings/api/api.settings";
import { ModelId } from "../components/api/models";
import { CacheUtils, CACHE_KEYS } from "@/lib/utils/cache-utils";

export default function AssistantPage({
  params
}: {
  params: { chatId: string }
}) {
  const chatId = params.chatId;
  const isNewChat = chatId === 'new';
  const router = useRouter();
  const searchParams = useSearchParams();
  const queryParam = searchParams.get('query');
  
  const currentChatIdRef = useRef<string | null>(isNewChat ? null : chatId);
  const [hasSubmitted, setHasSubmitted] = useState(false);
  const [initialInput, setInitialInput] = useState<string | null>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const [isMounted, setIsMounted] = useState(false);

  const [isCreatingChat, setIsCreatingChat] = useState(false);
  const [isJustCreated, setIsJustCreated] = useState(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem(`chat-${chatId}-just-created`) === 'true';
    }
    return false;
  });

  const [error, setError] = useState<string | null>(null);

  const { messages, append, isLoading, stop, setMessages } = useChat({
    api: '/api/chat',
    id: currentChatIdRef.current || undefined,
    initialMessages: [],
    sendExtraMessageFields: true,
    experimental_prepareRequestBody: ({ messages }) => {
      return {
        messages,
        chatId: currentChatIdRef.current
      };
    },
    onError: (error) => {
      console.error('Error in useChat:', error);
      let errorMessage = "An error occurred while processing your request.";
      
      try {
        const errorData = JSON.parse(error.message);
        
        if (errorData.error?.message === 'MESSAGE_LIMIT_EXCEEDED') {
          const details = errorData.error.details;
          
          if (details?.limitMessage && details?.messageId) {
            setMessages((prev) => {
              const userMessageExists = prev.some(msg => msg.role === 'user');
              
              if (!userMessageExists && currentChatIdRef.current) {
                return [
                  ...prev,
                  {
                    id: `user-msg-${Date.now()}`,
                    content: localStorage.getItem(`last-message-${currentChatIdRef.current}`) || "Your message",
                    role: 'user'
                  },
                  {
                    id: details.messageId,
                    content: details.limitMessage,
                    role: 'assistant',
                    isLimitMessage: true,
                    current: details.current,
                    limit: details.limit,
                    needsUpgrade: details.needsUpgrade
                  } as Message
                ];
              }
              
              return [
                ...prev,
                {
                  id: details.messageId,
                  content: details.limitMessage,
                  role: 'assistant',
                  isLimitMessage: true,
                  current: details.current,
                  limit: details.limit,
                  needsUpgrade: details.needsUpgrade
                } as Message
              ];
            });
            return;
          }
        } else if (errorData.error?.message === 'PREMIUM_MODEL_ACCESS_REQUIRED') {
          const details = errorData.error.details;
          
          if (details?.limitMessage && details?.messageId) {
            setMessages((prev) => {
              const userMessageExists = prev.some(msg => msg.role === 'user');
              
              if (!userMessageExists && currentChatIdRef.current) {
                return [
                  ...prev,
                  {
                    id: `user-msg-${Date.now()}`,
                    content: localStorage.getItem(`last-message-${currentChatIdRef.current}`) || "Your message",
                    role: 'user'
                  },
                  {
                    id: details.messageId,
                    content: details.limitMessage,
                    role: 'assistant',
                    isPremiumLimitMessage: true,
                    modelId: details.modelId,
                    modelName: details.modelName,
                    needsUpgrade: details.needsUpgrade
                  } as Message
                ];
              }
              
              return [
                ...prev,
                {
                  id: details.messageId,
                  content: details.limitMessage,
                  role: 'assistant',
                  isPremiumLimitMessage: true,
                  modelId: details.modelId,
                  modelName: details.modelName,
                  needsUpgrade: details.needsUpgrade
                } as Message
              ];
            });
            return;
          }
        } else if (errorData.error?.message) {
          errorMessage = errorData.error.message;
        }
      } catch (e) {
        errorMessage = error.message || errorMessage;
      }
      
      setError(errorMessage);
      setTimeout(() => setError(null), 5000);
    },
  });

  const [userTools, setUserTools] = useState<Record<string, any>>({});
  const [connectedTools, setConnectedTools] = useState<{ providerTag: string, logoUrl: string, isConnected: boolean }[]>([]);
  const [availableModels, setAvailableModels] = useState<string[]>([]);
  const [defaultModelId, setDefaultModelId] = useState<ModelId | undefined>(undefined);
  const [isLoadingModels, setIsLoadingModels] = useState(true);
  const [lastSelectedModelId, setLastSelectedModelId] = useState<ModelId | undefined>(undefined);
  const [playgroundSettingsData, setPlaygroundSettingsData] = useState<any>(null);

  const [chatState, setChatState] = useState<{
    id: string | null;
  }>({
    id: null
  });


  const [isLoadingMessages, setIsLoadingMessages] = useState(() => {
    return !isNewChat;
  });

  const [chatName, setChatName] = useState<string>("New Chat");

  useEffect(() => {
    const loadMessages = async () => {
      if (!isNewChat && chatId && !isJustCreated) {
        setIsLoadingMessages(true);
        try {
          const [existingMessages, chatData] = await Promise.all([
            getChatMessages(chatId),
            getChat(chatId)
          ]);
          
          if (chatData.name && chatData.name !== "undefined") {
            setChatName(chatData.name);
          } else {
            setChatName("New Chat");
          }
          
          // @ts-ignore
          const convertedMessages = existingMessages.map((msg) => {
            if (msg.sender === 'user') {
              return {
                id: msg.message_id,
                content: msg.message_text,
                role: 'user',
                parts: msg.parts,
                is_accurate: msg.is_accurate ?? null
              };
            }
            
            // @ts-ignore
            if (msg.sender === 'system' && msg.metadata?.isLimitMessage) {
              return {
                id: msg.message_id,
                content: msg.message_text,
                role: 'assistant' as const,
                isLimitMessage: true,
                // @ts-ignore 
                current: msg.metadata.current,
                // @ts-ignore 
                limit: msg.metadata.limit,
                // @ts-ignore
                needsUpgrade: msg.metadata.needsUpgrade
              };
            }

            // @ts-ignore
            if (msg.sender === 'system' && msg.metadata?.isPremiumLimitMessage) {
              return {
                id: msg.message_id,
                content: msg.message_text,
                role: 'assistant' as const,
                isPremiumLimitMessage: true,
                // @ts-ignore 
                modelId: msg.metadata.selectedModelId,
                // @ts-ignore 
                modelName: msg.metadata.modelName,
                // @ts-ignore
                needsUpgrade: true
              };
            }

            const updatedParts = msg.parts?.map((p) => {
              if ((p as any).type === 'tool-invocation') {
                const matchingInvocation = msg.metadata?.toolInvocations?.find(
                  (ti) => ti.toolCallId === (p as any).toolInvocation.toolCallId
                );

                return {
                  type: 'tool-invocation',
                  toolInvocation: {
                    ...(p as any).toolInvocation,
                    state: matchingInvocation?.state || 'pending',
                    result: matchingInvocation?.result ?? 'Processing...'
                  }
                };
              }
              return p;
            });

            return {
              id: msg.message_id,
              content: msg.message_text,
              role: 'assistant',
              parts: updatedParts,
              is_accurate: msg.is_accurate ?? null
            };
          });
          setMessages(convertedMessages as Message[]);
        } catch (error) {
          console.error('Error loading chat data:', error);
        } finally {
          setIsLoadingMessages(false);
        }
      }
    };

    loadMessages();
  }, [chatId, isNewChat, setMessages]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoadingModels(true);
        
        const [toolsData, connectedData, modelsData] = await Promise.all([
          CacheUtils.getUserTools(() => getUserToolsClient()),
          CacheUtils.getConnectedTools(() => getUserConnectedTools()),
          CacheUtils.getAvailableModels(() => getAvailableModels())
        ]);
        
        const playgroundSettings = await getUserPlaygroundSettings();
        
        setUserTools(toolsData);
        setConnectedTools(connectedData);
        setAvailableModels(modelsData.models);
        setPlaygroundSettingsData(playgroundSettings);
        
        if (playgroundSettings?.ai_model) {
          setDefaultModelId(playgroundSettings.ai_model as ModelId);
          setLastSelectedModelId(playgroundSettings.ai_model as ModelId);
        }
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setIsLoadingModels(false);
      }
    };

    fetchData();
  }, []);

  const handleNewMessage = async (value: string, modelId?: ModelId) => {
    try {
      if (modelId) {
        setLastSelectedModelId(modelId);
      }
      
      let chatId = currentChatIdRef.current;
      
      if (!chatId && isNewChat) {
        setIsCreatingChat(true);
        const newChat = await createChat({
          name: 'New Chat'
        });
        chatId = newChat.id;
        
        currentChatIdRef.current = chatId;
        router.replace(`/agent/${chatId}`);
        setHasSubmitted(true);

        localStorage.setItem(`chat-${chatId}-just-created`, 'true');
        setIsJustCreated(true);

        await new Promise(resolve => setTimeout(resolve, 0));
      }

      if (currentChatIdRef.current) {
        localStorage.setItem(`last-message-${currentChatIdRef.current}`, value);
      }

      const messageId = `msg-${Date.now()}`;
      await createChatMessage({
        message_id: messageId,
        chat_id: currentChatIdRef.current || chatId || '',
        sender: 'user',
        message_text: value,
        metadata: modelId ? { 
          selectedModelId: modelId
        } : undefined
      });

      await append({
        id: messageId,
        content: value,
        role: 'user'
      });

    } catch (error) {
      console.error('Error in handleNewMessage:', error);
    } finally {
      setIsCreatingChat(false);
    }
  };

  useEffect(() => {
    if (messages.length > 0 && 
        messages[messages.length - 1].role === 'assistant' && 
        !isLoading) {
      if (currentChatIdRef.current) {
        localStorage.removeItem(`chat-${currentChatIdRef.current}-just-created`);
        setIsJustCreated(false);
        setIsLoadingMessages(false);
      }
    }
  }, [messages, isLoading]);

  useEffect(() => {
    if (messages.length > 0 && 
        messages[messages.length - 1].role === 'assistant' && 
        !isLoading) {
      const fetchTitleAndUpdate = async () => {
        if (isJustCreated && messages[0]?.role === 'user') {
          try {
            const titleData = await updateChatTitle(
              currentChatIdRef.current!,
              messages[0].content
            );
            if (titleData.title) {
              setChatName(titleData.title);
            }
          } catch (error) {
            console.error('Error updating chat title:', error);
          }
        }
      };
      
      fetchTitleAndUpdate();
    }
  }, [messages, isLoading, isJustCreated]);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  useEffect(() => {
    if (isNewChat && queryParam) {
      setInitialInput(queryParam);
    }
  }, [isNewChat, queryParam]);

  useEffect(() => {
    if (isMounted && typeof window !== 'undefined' && isNewChat && queryParam && !hasSubmitted) {
      if (queryParam.startsWith('Run Flow')) {
        const timer = setTimeout(() => {
          if (!hasSubmitted) {
            handleNewMessage(queryParam);
          }
        }, 1000);
        
        return () => clearTimeout(timer);
      }
    }
  }, [isMounted, isNewChat, queryParam, hasSubmitted]);

  const handleModelChange = async (modelId: ModelId) => {
    setLastSelectedModelId(modelId);
    
    try {
      const updatedSettings = {
        agent_prompt: playgroundSettingsData?.agent_prompt || '',
        ai_model: modelId,
        api_key_provider_name: playgroundSettingsData?.api_key_provider_name || '',
        api_key: playgroundSettingsData?.api_key || '',
        api_key_enabled: playgroundSettingsData?.api_key_enabled || false
      };
      
      const result = await saveUserPlaygroundSettings(updatedSettings);
      
      // Обновляем только кэш моделей
      if (availableModels) {
        CacheUtils.updateCache(CACHE_KEYS.AVAILABLE_MODELS, {
          models: availableModels,
          defaultModelId: modelId
        });
      }
      
      setPlaygroundSettingsData(result);
    } catch (error) {
      console.error('Error saving model preference:', error);
    }
  };

  return (
    <div className="flex h-full">
      <div className="flex-1 flex flex-col relative h-[100vh] w-full">
        <Header 
          isShowChat={!isNewChat && !isLoadingMessages} 
          chatName={!isNewChat ? chatName : "New Chat"}
        />
        
        {error && (
          <div className="fixed top-4 left-1/2 transform -translate-x-1/2 z-50 flex items-center gap-2 bg-destructive text-destructive-foreground px-4 py-2 rounded-md shadow-lg">
            <AlertCircle size={16} />
            <span>{error}</span>
          </div>
        )}

        {(isLoadingMessages && !isJustCreated && !isNewChat) ? (
          <div className="flex-1 flex items-center justify-center">
            <Loader2 className="animate-spin" />
          </div>
        ) : (isNewChat && !hasSubmitted) ? (
          <AssistantEmptyState
            onSubmit={handleNewMessage}
            isLoading={false}
            onStop={stop}
            userTools={userTools}
            connectedTools={connectedTools}
            onToolClick={() => {}}
            initialInput={initialInput}
            availableModels={availableModels}
            defaultModelId={defaultModelId}
            onModelChange={handleModelChange}
          />
        ) : (
          <>
            <ScrollArea className="flex-1">
              <ChatMessages 
                chatId={chatId}
                messages={messages as Message[]}
                isLoading={isLoading}
                onSendMessage={async (message: string) => {
                  if (lastSelectedModelId) {
                    const messageId = `msg-${Date.now()}`;
                    await createChatMessage({
                      message_id: messageId,
                      chat_id: currentChatIdRef.current || '',
                      sender: 'user',
                      message_text: message,
                      metadata: { 
                        selectedModelId: lastSelectedModelId 
                      }
                    });
                  }
                  
                  await append({
                    content: message,
                    role: 'user'
                  });
                }}
              />
            </ScrollArea>

            <div className="sticky bottom-0 bg-background">
              <div className="flex flex-col p-4 mx-auto w-full max-w-5xl">
                
                <AIInputWithSearch
                  ref={inputRef}
                  placeholder={"Ask about anything..."}
                  onSubmit={handleNewMessage}
                  className="max-w-none"
                  isLoading={isLoading}
                  onStop={stop}
                  userTools={userTools}
                  initialInput={initialInput}
                  availableModels={availableModels}
                  defaultModelId={defaultModelId}
                  onModelChange={handleModelChange}
                />
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  )
}