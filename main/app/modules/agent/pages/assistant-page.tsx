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
import { useRouter } from "next/navigation";
import { createChatMessage } from "../api/api.agent";
import { getChatMessages } from "../api/api.agent";
import { Loader2 } from "lucide-react"
import { getChat } from "../api/api.agent";
import { getUserToolsClient } from "@/lib/utils/get-user-tools-client";
import { getUserConnectedTools } from "@/app/modules/integrations/api/api.integrations";
import { updateChatTitle } from "../api/api.agent";

interface ExtendedMessage extends Message {
  toolCalls?: any[];
  toolResults?: any[];
  toolInvocations?: any[];
  finishReason?: string;
  is_accurate?: boolean | null;
}

export default function AssistantPage({
  params
}: {
  params: { chatId: string }
}) {
  const chatId = params.chatId;
  const isNewChat = chatId === 'new';
  const router = useRouter();
  
  const currentChatIdRef = useRef<string | null>(isNewChat ? null : chatId);
  const [hasSubmitted, setHasSubmitted] = useState(false);

  const [isCreatingChat, setIsCreatingChat] = useState(false);
  const [isJustCreated, setIsJustCreated] = useState(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem(`chat-${chatId}-just-created`) === 'true';
    }
    return false;
  });

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
    },
  });

  const [userTools, setUserTools] = useState<Record<string, any>>({});
  const [connectedTools, setConnectedTools] = useState<{ providerTag: string, logoUrl: string, isConnected: boolean }[]>([]);
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
          
          const convertedMessages = existingMessages.map((msg) => {

            if (msg.sender !== 'assistant') {
              return {
                id: msg.message_id,
                content: msg.message_text,
                role: 'user',
                parts: msg.parts,
                is_accurate: msg.is_accurate ?? null
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

  const handleNewMessage = async (value: string) => {
    try {
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

      const messageId = `msg-${Date.now()}`;
      await createChatMessage({
        message_id: messageId,
        chat_id: currentChatIdRef.current || chatId || '',
        sender: 'user',
        message_text: value,
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
    const fetchTools = async () => {
      try {
        const [tools, connected] = await Promise.all([
          getUserToolsClient(),
          getUserConnectedTools()
        ]);
        setUserTools(tools);
        setConnectedTools(connected);
      } catch (error) {
        console.error('Error fetching tools:', error);
      }
    };

    fetchTools();
  }, []);

  return (
    <div className="flex h-full">
      <div className="flex-1 flex flex-col relative h-[100vh] w-full">
        <Header 
          isShowChat={!isNewChat && !isLoadingMessages} 
          chatName={!isNewChat ? chatName : "New Chat"}
        />
        
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
          />
        ) : (
          <>
            <ScrollArea className="flex-1">
              <ChatMessages 
                chatId={chatId}
                messages={messages as Message[]}
                isLoading={isLoading}
                onSendMessage={async (message: string) => {
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
                  placeholder={"Ask about anything..."}
                  onSubmit={handleNewMessage}
                  className="max-w-none"
                  isLoading={isLoading}
                  onStop={stop}
                  userTools={userTools}
                />
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  )
}