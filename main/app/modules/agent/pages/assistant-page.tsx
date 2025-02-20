"use client"
import React, { useState, useEffect, useRef } from "react"
import { ScrollArea } from "@/components/ui/scroll-area"
import { useChat } from 'ai/react'
import { AIInputWithSearch } from "../components/input/ai-input"
import { Header } from "../../general/components/header"
import FileUpload from "../components/input/file-uploader"
import { ChatMessages } from "../components/messages/chat-messages"
import { type Message } from 'ai/react'
import { getUserToolsClient } from "@/lib/utils/get-user-tools-client";
import { AssistantEmptyState } from "./assistant-empty-state";
import { getUserConnectedTools } from "@/app/modules/integrations/api/api.integrantions"
import { useFileHandling } from "../components/input/file-handler"
import { createChat } from "../components/api/api.agent";
import { useRouter } from "next/navigation";
import { createChatMessage } from "../components/api/api.agent";
import { getChatMessages } from "../components/api/api.agent";
import { Loader2 } from "lucide-react"
import { getChat } from "../components/api/api.agent";
import { useToolHandling } from '@/hooks/use-tool-handling';

interface ExtendedMessage extends Message {
  toolCalls?: any[];
  toolResults?: any[];
  toolInvocations?: any[];
  finishReason?: string;
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

  const [showSuggestions, setShowSuggestions] = useState(true);
  const [messageAttachments, setMessageAttachments] = useState<{
    [messageId: string]: {
      files: File[];
      previews: { [filename: string]: string };
    }
  }>({});
  const [followUpSuggestions, setFollowUpSuggestions] = useState<string[]>([]);
  const [userTools, setUserTools] = useState<Record<string, any>>({});
  const [connectedTools, setConnectedTools] = useState<{ providerTag: string, logoUrl: string }[]>([]);
  const [chatState, setChatState] = useState<{
    id: string | null;
  }>({
    id: null
  });

  const allowedFileTypes = ['png', 'jpg', 'jpeg', 'txt', 'doc', 'docx', 'rtf'];
  
  const {
    isDragging,
    uploadedFiles,
    previews,
    fileMetadata,
    sandboxId,
    tableContent,
    textContent,
    handlers
  } = useFileHandling(allowedFileTypes);

  const [isLoadingMessages, setIsLoadingMessages] = useState(() => {
    return !isNewChat;
  });

  const [chatName, setChatName] = useState<string>("New Chat");

  useEffect(() => {
    const loadMessages = async () => {
      if (!isNewChat && chatId) {
        setIsLoadingMessages(true);
        try {
          const [existingMessages, chatData] = await Promise.all([
            getChatMessages(chatId),
            getChat(chatId)
          ]);
          console.log(getChatMessages(chatId))
          
          if (chatData.name && chatData.name !== "undefined") {
            setChatName(chatData.name);
          } else {
            setChatName("New Chat");
          }
          
          const convertedMessages = existingMessages.map((msg) => {
            console.log('Processing message:', msg);
            console.log('Message parts:', msg.parts);
            if (msg.metadata?.toolInvocations) {
              console.log('Tool invocations:', msg.metadata.toolInvocations);
            }

            if (msg.sender !== 'assistant') {
              return {
                id: msg.message_id,
                content: msg.message_text,
                role: 'user',
                parts: msg.parts
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
              parts: updatedParts
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
    if (messages.length > 0 && uploadedFiles) {
      const lastMessage = messages[messages.length - 1];
      if (lastMessage.role === 'user') {
        setMessageAttachments(prev => ({
          ...prev,
          [lastMessage.id]: {
            files: Array.from(uploadedFiles),
            previews: { ...previews }
          }
        }));
      }
    }
  }, [messages, uploadedFiles]);

  const handleNewMessage = async (value: string) => {
    try {
      console.log('Creating new user message:', value);
      let chatId = currentChatIdRef.current;
      
      if (!chatId && isNewChat) {
        setIsCreatingChat(true);
        const newChat = await createChat({
          name: 'New Chat'
        });
        console.log('Created new chat:', newChat);
        chatId = newChat.id;
        
        currentChatIdRef.current = chatId;
        router.replace(`/agent/${chatId}`);

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
      console.log('Successfully saved user message to database');

      await append({
        id: messageId,
        content: value,
        role: 'user'
      });
      console.log('Message appended to chat interface');

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
      }
    }
  }, [messages, isLoading]);

  useEffect(() => {
    if (messages.length > 0 && 
        messages[messages.length - 1].role === 'assistant' && 
        !isLoading) {
      const fetchTitleAndUpdate = async () => {
        if (isJustCreated && messages[0]?.role === 'user') {
          const titleResponse = await fetch('/api/chat-title', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
              chatId: currentChatIdRef.current,
              firstMessage: messages[0].content 
            }),
          });

          const titleData = await titleResponse.json();
          if (titleData.title) {
            setChatName(titleData.title);
          }
        }
      };
      
      fetchTitleAndUpdate();
    }
  }, [messages, isLoading, isJustCreated]);

  const handleShowSuggestions = (show: boolean) => {
    setShowSuggestions(show);
  };

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
        
        {isLoadingMessages && !isJustCreated ? (
          <div className="flex-1 flex items-center justify-center">
            <Loader2 className="animate-spin" />
          </div>
        ) : isNewChat ? (
          <AssistantEmptyState
            onSubmit={handleNewMessage}
            onShowSuggestions={handleShowSuggestions}
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
                messages={messages as Message[]}
                messageAttachments={messageAttachments}
                isLoading={isLoading}
                sandboxId={sandboxId}
                onEditMessage={async (messageId: string, newContent: string) => {
                  const messageIndex = messages.findIndex(m => m.id === messageId);
                  if (messageIndex === -1) return;

                  const newMessages = messages.slice(0, messageIndex);
                  setMessages(newMessages);
                  
                  await append({
                    content: newContent,
                    role: 'user'
                  });
                }}
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
                
                {(uploadedFiles || isDragging) && 
                 !isLoading && 
                 (!messages.length || messages[messages.length - 1].role === 'assistant') && (
                  <FileUpload
                    onFileSelect={handlers.handleFileSelect}
                    onFileRemove={handlers.handleFileRemove}
                    onTableFileSelect={handlers.handleTableFileSelect}
                    onTextFileSelect={handlers.handleTextFileSelect}
                    onUploadSuccess={handlers.handleUploadSuccess}
                    uploadedFiles={uploadedFiles ? Array.from(uploadedFiles) : []}
                    sandboxId={sandboxId}
                    allowedTypes={allowedFileTypes}
                    maxSize={5 * 1024 * 1024}
                  />
                )}
                
                <AIInputWithSearch
                  placeholder={"Ask about anything..."}
                  onSubmit={handleNewMessage}
                  className="max-w-none"
                  isLoading={isLoading}
                  onStop={stop}
                  onShowSuggestions={handleShowSuggestions}
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