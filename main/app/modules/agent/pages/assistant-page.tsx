"use client"
import React, { useState, useEffect} from "react"
import { ScrollArea } from "@/components/ui/scroll-area"
import { useChat } from 'ai/react'
import { AIInputWithSearch } from "../components/input/ai-input"
import { Suggestions } from "../components/suggestions/suggestions"
import { SuggestionsDummyAgent } from "../components/suggestions/suggestions-dummy"
import { Header } from "../../general/components/header"
import FileUpload from "../components/input/file-uploader"
import { ChatMessages } from "../components/messages/chat-messages"
import { SuggestionInputs } from "../components/suggestions/suggestion-inputs"
import { type Message } from 'ai/react'
import { toast } from "sonner"
import { X } from "lucide-react"
import { getUserToolsClient } from "@/lib/utils/get-user-tools-client";
import { AssistantEmptyState } from "./assistant-empty-state";
import { getUserConnectedTools } from "@/app/modules/integrations/api/api.integrantions"

export default function AssistantPage() {
  const { messages, append, isLoading, stop, setMessages } = useChat({
    api: '/api/chat',
    id: 'assistant-chat',
    initialMessages: [],
  });

  const [showSuggestions, setShowSuggestions] = useState(true);
  const [isDragging, setIsDragging] = useState(false);
  const dragCounter = React.useRef(0);
  const [uploadedFiles, setUploadedFiles] = useState<FileList | null>(null);
  const [previews, setPreviews] = useState<{[key: string]: string}>({});
  const [messageAttachments, setMessageAttachments] = useState<{
    [messageId: string]: {
      files: File[];
      previews: { [filename: string]: string };
    }
  }>({});
  const [tableContent, setTableContent] = useState<string | null>(null);
  const [textContent, setTextContent] = useState<string | null>(null);
  const [fileMetadata, setFileMetadata] = useState<{
    sandboxId: string;
    fileName: string;
    path: string;
  } | null>(null);
  const [sandboxId, setSandboxId] = useState<string | null>(null);
  const [followUpSuggestions, setFollowUpSuggestions] = useState<string[]>([]);
  const [userTools, setUserTools] = useState<Record<string, any>>({});
  const [connectedTools, setConnectedTools] = useState<{ providerTag: string, logoUrl: string }[]>([]);

  const allowedFileTypes = ['png', 'jpg', 'jpeg', 'txt', 'doc', 'docx', 'rtf'];

  useEffect(() => {
    if (!uploadedFiles) return;

    Array.from(uploadedFiles).forEach(file => {
      if (!previews[file.name] && file.type.startsWith('image/')) {
        const objectUrl = URL.createObjectURL(file);
        setPreviews(prev => ({
          ...prev,
          [file.name]: objectUrl
        }));
      }
    });

    return () => {
      Object.values(previews).forEach(url => URL.revokeObjectURL(url));
    };
  }, [uploadedFiles]);

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
        setIsDragging(false);
      }
    }
  }, [messages, uploadedFiles]);

  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault();
    dragCounter.current += 1;
    if (dragCounter.current === 1) {
      setIsDragging(true);
    }
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    dragCounter.current -= 1;
    if (dragCounter.current === 0) {
      setIsDragging(false);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    dragCounter.current = 0;
    setIsDragging(false);
    
    const files = e.dataTransfer.files;
    if (!files || files.length === 0) return;

    const file = files[0];
    const fileType = file.name.split('.').pop()?.toLowerCase();
    const allowedImageTypes = ['png', 'jpg', 'jpeg'];
    const allowedTextTypes = ['txt', 'doc', 'docx', 'rtf'];
    
    if (fileType === 'csv' || fileType === 'xlsx' || fileType === 'xls' || fileType === 'sql') {
      toast.error(`File type .${fileType} is not supported`, {
        action: {
          label: <X className="h-4 w-4" />,
          onClick: () => console.log("OK clicked")
        }
      });
      return;
    }

    if (!allowedImageTypes.includes(fileType || '') && 
        !allowedTextTypes.includes(fileType || '')) {
      toast.error(`File type .${fileType} is not supported`, {
        action: {
          label: <X className="h-4 w-4" />,
          onClick: () => console.log("OK clicked")
        }
      });
      return;
    }

    handleFileSelect(files);
  };

  const handleUploadSuccess = (data: { sandboxId: string, fileName: string, path: string }) => {
    setSandboxId(data.sandboxId);
    setFileMetadata(data);
  };

  const handleNewMessage = async (value: string) => {
    setShowSuggestions(false);
    setIsDragging(false);
    setFollowUpSuggestions([]);
    
    let messageContent = value;
    
    if (fileMetadata) {
      messageContent = `${value}\n\nFile Information:\nFile: ${fileMetadata.fileName}\nSandbox ID: ${fileMetadata.sandboxId}\nPath: ${fileMetadata.path}`;
    } else if (tableContent || textContent) {
      const contentType = tableContent ? 'Table' : 'Text';
      messageContent = `${value}\n\n${contentType} content:\n${tableContent || textContent}`;
    }

    const options: {
      experimental_attachments?: FileList;
    } = {};

    if (uploadedFiles && Array.from(uploadedFiles).some(file => file.type.startsWith('image/'))) {
      options.experimental_attachments = uploadedFiles;
    }

    await append({
      content: messageContent,
      role: 'user'
    }, Object.keys(options).length ? options : undefined);

    handleFileRemove();
    setFileMetadata(null);
    setTableContent(null);
    setTextContent(null);
  };

  useEffect(() => {
    if (messages.length > 0 && 
        messages[messages.length - 1].role === 'assistant' && 
        !isLoading) {
      const fetchSuggestions = async () => {
        const response = await fetch('/api/suggestions', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ messages }),
        });
        const data = await response.json();
        setFollowUpSuggestions(data.suggestions);
      };
      
      fetchSuggestions();
    }
  }, [messages, isLoading]);

  const handleFileSelect = (files: FileList) => {
    setUploadedFiles(files);
  };

  const handleFileRemove = () => {
    if (uploadedFiles) {
      Array.from(uploadedFiles).forEach(file => {
        if (previews[file.name]) {
          URL.revokeObjectURL(previews[file.name]);
        }
      });
    }
    setPreviews({});
    setUploadedFiles(null);
  };

  const handleTableFileSelect = async (markdown: string, fileName: string) => {
    setTableContent(markdown);
  };

  const handleTextFileSelect = async (text: string, fileName: string) => {
    setTextContent(text);
  };

  const handleEditMessage = async (messageId: string, newContent: string) => {
    const messageIndex = messages.findIndex(m => m.id === messageId);
    if (messageIndex === -1) return;

    const newMessages = messages.slice(0, messageIndex);
    setMessages(newMessages);
    
    await append({
      content: newContent,
      role: 'user'
    });

  };

  const getCurrentSuggestions = () => {
    return SuggestionsDummyAgent;
  };

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
    <div 
      className="flex h-full"
      onDragEnter={handleDragEnter}
      onDragLeave={handleDragLeave}
      onDragOver={handleDragOver}
      onDrop={handleDrop}
    >
      <div className="flex-1 flex flex-col relative h-[100vh] w-full">
        {messages.length === 0 ? (
          <>
            <Header isShowChat={true} />
            <AssistantEmptyState
              onSubmit={handleNewMessage}
              onShowSuggestions={handleShowSuggestions}
              isLoading={isLoading}
              onStop={stop}
              userTools={userTools}
              connectedTools={connectedTools}
              onToolClick={() => {}}
            />
          </>
        ) : (
          <>
            <Header isShowChat={true} chatName="New Chat" />
            <ScrollArea className="flex-1">
              <ChatMessages 
                messages={messages as Message[]}
                messageAttachments={messageAttachments}
                isLoading={isLoading}
                sandboxId={sandboxId}
                onEditMessage={handleEditMessage}
                onSendMessage={async (message: string) => {
                  await append({
                    content: message,
                    role: 'user'
                  });
                }}
              />
            </ScrollArea>

            <div className="sticky bottom-0 bg-background">
              <div className="flex flex-col gap-2 p-4 mx-auto w-full max-w-5xl">
                <Suggestions
                  items={getCurrentSuggestions()}
                  onSelect={handleNewMessage}
                  visible={showSuggestions && messages.length === 0}
                />
                
                <SuggestionInputs
                  suggestions={followUpSuggestions}
                  onSendMessage={handleNewMessage}
                  visible={messages.length > 0 && 
                    messages[messages.length - 1].role === 'assistant' && 
                    !isLoading}
                />
                
                {(uploadedFiles || isDragging) && 
                 !isLoading && 
                 (!messages.length || messages[messages.length - 1].role === 'assistant') && (
                  <FileUpload
                    onFileSelect={handleFileSelect}
                    onFileRemove={handleFileRemove}
                    onTableFileSelect={handleTableFileSelect}
                    onTextFileSelect={handleTextFileSelect}
                    onUploadSuccess={handleUploadSuccess}
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
