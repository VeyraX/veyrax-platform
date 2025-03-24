import { MessageFormatter } from "./message-formatter"
import { Button } from "@/components/ui/button"
import { ThumbsDown, ThumbsUp, Copy, Check } from "lucide-react"
import React, { useRef } from "react"
import { Skeleton } from "@/components/ui/skeleton"
import { type Message } from 'ai/react'
import { updateMessageAccuracy } from "../../api/api.agent"
import { useAutoScroll } from "@/hooks/use-chat-scroll"
import DynamicComponentRender from "../tools/common/dymanic-component-render"
import { FlowChatEmptyState } from "@/app/modules/flows/components/test/flow-chat-test-empty-state"

interface ExtendedMessage extends Message {
  image_url?: string;
  is_accurate?: boolean | null;
}

interface ChatMessagesProps {
  messages: ExtendedMessage[]
  isLoading: boolean
  onSendMessage?: (message: string) => void
  isInitialLoading?: boolean
  chatId: string
  isFlow?: boolean
  hideRatings?: boolean
}

function parseMessageContent(content: string) {
  const tableMarker = "\n\nTable content:";
  const textMarker = "\n\nText content:";
  const fileMarker = "\n\nFile Information:";
  const referenceDocMarker = "\n\nReference Documentation:";
  
  let cleanContent = content;
  
  const tableIndex = cleanContent.indexOf(tableMarker);
  if (tableIndex !== -1) {
    cleanContent = cleanContent.substring(0, tableIndex);
  }
  
  const textIndex = cleanContent.indexOf(textMarker);
  if (textIndex !== -1) {
    cleanContent = cleanContent.substring(0, textIndex);
  }
  
  const fileIndex = cleanContent.indexOf(fileMarker);
  if (fileIndex !== -1) {
    cleanContent = cleanContent.substring(0, fileIndex);
  }
  
  const referenceDocIndex = cleanContent.indexOf(referenceDocMarker);
  if (referenceDocIndex !== -1) {
    cleanContent = cleanContent.substring(0, referenceDocIndex);
  }
  
  cleanContent = cleanContent.trim();
  
  return cleanContent;
}

export function ChatMessages({ messages, isLoading, onSendMessage, isInitialLoading, chatId, isFlow = false, hideRatings = false }: ChatMessagesProps) {
  const [copiedMessageId, setCopiedMessageId] = React.useState<string | null>(null);
  const [ratedMessages, setRatedMessages] = React.useState<Set<string>>(new Set());
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const { shouldAutoScroll } = useAutoScroll({
    messagesEndRef,
    isLoading,
    messages
  });

  const handleRate = async (messageId: string, chatId: string, isAccurate: boolean) => {
    try {
      await updateMessageAccuracy(messageId, chatId, isAccurate);
      setRatedMessages(prev => {
        const newSet = new Set(prev);
        newSet.add(messageId);
        return newSet;
      });
    } catch (error) {
      console.error('Error updating message accuracy:', error);
    }
  };

  const handleCopy = async (messageId: string, content: string) => {
    await navigator.clipboard.writeText(parseMessageContent(content));
    setCopiedMessageId(messageId);
    setTimeout(() => setCopiedMessageId(null), 2000);
  };

  return (
    <div className={`flex flex-col gap-8 p-4 max-w-5xl mx-auto w-full ${isFlow ? '' : 'overflow-y-auto'} relative h-full`}>
      {messages.length === 0 && isFlow ? (
        <div className="flex-grow flex items-center justify-center min-h-[300px]">
          <FlowChatEmptyState />
        </div>
      ) : (
        messages.map((message, index) => {
          const showAvatar = index === 0 || messages[index - 1].role !== message.role;
          const isLastAssistantMessage = message.role === 'assistant' && 
            (index === messages.length - 1 || messages[index + 1]?.role === 'user');
          const isLastMessage = index === messages.length - 1;
          
          return (
            <div 
              key={message.id}
              className={`flex gap-4 group ${message.role === 'user' ? 'justify-end' : ''}`}
            >
              <div className={`grid gap-1.5 ${
                message.role === 'user' 
                  ? 'max-w-[75%]'
                  : 'w-full'
              }`}>
                <div className="text-sm leading-relaxed relative">
                  <div className="flex justify-between items-start gap-2">
                    <div className={`${
                      message.role === 'user' 
                        ? 'bg-[#2A2B2C] text-white rounded-3xl rounded-br-sm px-4 py-2 text-[15px] min-w-[60px] text-left'
                        : ''
                    } flex-1`}>
                      {(message.parts?.length ?? 0) > 0 ? (
                        message.parts?.map((part, partIndex) => {
                          if (part.type === 'text') {
                            return (
                              <MessageFormatter 
                                key={partIndex} 
                                content={part.text} 
                              />
                            );
                          }
                          if (part.type === 'tool-invocation') {
                            const { toolCallId, toolName, args, state } = part.toolInvocation;
                            const result = part.toolInvocation.state === 'result' ? part.toolInvocation.result : undefined;

                            return (
                              <div key={toolCallId} className="py-4">
                                {(() => {
                                  switch(toolName) {
                                    case 'tool_call':
                                      return (
                                          <div className="max-w-3xl w-full">
                                            {['partial-call', 'call'].includes(state) ? (
                                              <Skeleton className="h-32 w-full" />
                                            ) : (
                                              result?.success && result.result?.component && (
                                                <DynamicComponentRender component={result.result.component} />
                                              )
                                            )}
                                          </div>
                                      );
                                    
                                    case 'tool_call_test_flow':
                                      return (
                                        <div className="flex items-center gap-2">
                                          {['partial-call', 'call'].includes(state) ? (
                                            <div className="flex items-center gap-2">
                                              <div className="animate-spin rounded-full h-4 w-4 border-2 border-primary border-t-transparent"></div>
                                              <span>Running {args?.params?.tool || ""} {args?.params?.method || ""}...</span>
                                            </div>
                                          ) : (
                                            <div className="flex items-center gap-2">
                                              <Check className="h-4 w-4" />
                                              <span>Completed</span>
                                            </div>
                                          )}
                                        </div>
                                      );
                                    
                                    case 'flow_improve_description':
                                    case 'flow_generate':
                                      return (
                                        <div className="flex items-center gap-2">
                                          {['partial-call', 'call'].includes(state) ? (
                                            <div className="flex items-center gap-2">
                                              <div className="animate-spin rounded-full h-4 w-4 border-2 border-primary border-t-transparent"></div>
                                              <span>Generating flow...</span>
                                            </div>
                                          ) : (
                                            <div className="flex items-center gap-2">
                                              <Check className="h-4 w-4" />
                                              <span>Generated</span>
                                            </div>
                                          )}
                                        </div>
                                      );
                                      
                                    default:
                                      return null;
                                  }
                                })()}
                              </div>
                            );
                          }
                          return null;
                        })
                      ) : (
                        <MessageFormatter content={message.content} />
                      )}
                    </div>
                  </div>
                  <div className="flex justify-end gap-2 mt-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    {message.role === 'user' && (
                      <Button
                        variant="ghost"
                        size="icon"
                        className="text-muted-foreground hover:text-foreground h-8 w-8 p-0 rounded-full hover:bg-muted"
                        onClick={() => handleCopy(message.id, message.content)}
                      >
                        {copiedMessageId === message.id ? (
                          <Check className="h-4 w-4 text-muted-foreground" />
                        ) : (
                          <Copy className="h-4 w-4 text-muted-foreground" />
                        )}
                      </Button>
                    )}
                  </div>
                </div>

                {isLastAssistantMessage && 
                 !isLoading && 
                 (!message.hasOwnProperty('is_accurate') || message.is_accurate === null) &&
                 !ratedMessages.has(message.id) && 
                 !hideRatings && (
                  <div className="flex gap-1 -translate-y-4">
                    <Button 
                      variant="ghost" 
                      size="icon" 
                      className="text-muted-foreground hover:text-foreground h-8 w-8 p-0 rounded-full hover:bg-muted"
                      onClick={() => handleRate(message.id, chatId, true)}
                    >
                      <ThumbsUp className="h-4 w-4" />
                    </Button>
                    <Button 
                      variant="ghost" 
                      size="icon" 
                      className="text-muted-foreground hover:text-foreground h-8 w-8 p-0 rounded-full hover:bg-muted"
                      onClick={() => handleRate(message.id, chatId, false)}
                    >
                      <ThumbsDown className="h-4 w-4" />
                    </Button>
                  </div>
                )}
              </div>
            </div>
          );
        })
      )}

      {isLoading && messages[messages.length - 1]?.role === 'user' && (
        <div className="flex gap-4">
          <div className="flex items-center">
            <span className="text-sm text-muted-foreground">is thinking...</span>
          </div>
        </div>
      )}

      <div ref={messagesEndRef} style={{ height: "1px" }} />
    </div>
  )
}