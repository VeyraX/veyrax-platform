import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { MessageFormatter } from "./message-formatter"
import { Button } from "@/components/ui/button"
import { ThumbsDown, ThumbsUp, Pencil } from "lucide-react"
import React from "react"
import EventCard from "../tools/eventbrite/event-cards/event-card"
import { EventDetailCard } from "../tools/eventbrite/event-card-detail/event-card-detail"
import { Skeleton } from "@/components/ui/skeleton"
import type { Event } from "../tools/eventbrite/event-card-types"
import { Card, CardHeader, CardContent, CardFooter } from "@/components/ui/card"
import { useChatScroll } from "@/hooks/use-chat-scroll"
import { EditMessage } from "./chat-messages-edit-message"
import { StripeProvider } from "../tools/stripe/stripe-provider"
import { PaymentForm } from "../tools/stripe/stripe-paymenet-card"
import { EventCardsList } from "../tools/eventbrite/event-cards/event-card-list"
import ProgressStates from "../tools/generate-component/generate-component-loading-bar"
import { CalendarView } from "../tools/calendar/calendar-view"

interface ChatMessagesProps {
  messages: any[]
  messageAttachments: {
    [messageId: string]: {
      files: File[]
      previews: { [filename: string]: string }
    }
  }
  isLoading: boolean
  sandboxId: string | null
  onEditMessage?: (messageId: string, content: string) => void
  onSendMessage?: (message: string) => void
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

export function ChatMessages({ messages, messageAttachments, isLoading, sandboxId, onEditMessage, onSendMessage }: ChatMessagesProps) {
  const [ratedMessageIds, setRatedMessageIds] = React.useState<Set<string>>(new Set());
  const [editingMessageId, setEditingMessageId] = React.useState<string | null>(null);
  const { containerRef, lastMessageRef } = useChatScroll(messages, isLoading);

  const handleRate = (messageId: string) => {
    setRatedMessageIds(prev => new Set(prev).add(messageId));
  };

  const handleEditStart = (message: any) => {
    setEditingMessageId(message.id);
  };

  const handleEditSave = async (messageId: string, content: string) => {
    await onEditMessage?.(messageId, content);
    setEditingMessageId(null);
  };

  const handleEditCancel = () => {
    setEditingMessageId(null);
  };

  return (
    <div 
      ref={containerRef}
      className="flex flex-col gap-8 p-4 max-w-5xl mx-auto w-full overflow-y-auto"
    >
      {messages.map((message, index) => {
        const showAvatar = index === 0 || messages[index - 1].role !== message.role;
        const currentAttachments = messageAttachments[message.id];
        const isLastAssistantMessage = message.role === 'assistant' && 
          (index === messages.length - 1 || messages[index + 1]?.role === 'user');
        const isLastMessage = index === messages.length - 1;
        
        return (
          <div 
            key={message.id} 
            ref={isLastMessage ? lastMessageRef : undefined}
            className="flex gap-4 group"
          >
            {showAvatar ? (
              <Avatar className="h-8 w-8">
                <AvatarImage src={message.role === 'user' ? '/placeholder.svg' : '/placeholder.svg'} />
                <AvatarFallback>
                  {message.role === 'user' ? 'U' : 'A'}
                </AvatarFallback>
              </Avatar>
            ) : (
              <div className="w-8" />
            )}
            <div className="grid gap-1.5 w-full">
              {message.role === 'user' && currentAttachments && (
                <div className="flex flex-wrap gap-1.5 mb-2">
                  {currentAttachments.files.map((file: File) => (
                    <div 
                      key={file.name} 
                      className="relative bg-background border border-border rounded-xl p-1 w-[100px]"
                    >
                      <div className="flex flex-col items-center gap-0.5">
                        {file.type.startsWith('image/') && currentAttachments.previews[file.name] ? (
                          <div className="relative h-10 w-10 bg-muted/30 rounded-lg overflow-hidden">
                            <img 
                              src={currentAttachments.previews[file.name]} 
                              alt={file.name} 
                              className="absolute inset-0 h-full w-full object-contain"
                            />
                          </div>
                        ) : (
                          <div className={`h-10 w-10 rounded-lg flex items-center justify-center text-xs font-medium
                            ${file.name.split('.').pop()?.toLowerCase() === 'xlsx' || 
                              file.name.split('.').pop()?.toLowerCase() === 'xls' || 
                              file.name.split('.').pop()?.toLowerCase() === 'csv' 
                              ? 'bg-green-100 text-green-700'
                              : file.name.split('.').pop()?.toLowerCase() === 'doc' ||
                                file.name.split('.').pop()?.toLowerCase() === 'docx' ||
                                file.name.split('.').pop()?.toLowerCase() === 'rtf'
                              ? 'bg-blue-100 text-blue-700'
                              : 'bg-muted'}`}>
                            {file.name.split('.').pop()?.toUpperCase()}
                          </div>
                        )}
                        <span className="text-[10px] text-center w-full truncate px-0.5 text-muted-foreground">
                          {file.name}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
              <div className="text-sm leading-relaxed relative">
                {editingMessageId === message.id ? (
                  <EditMessage
                    content={parseMessageContent(message.content)}
                    onSave={(content: string) => handleEditSave(message.id, content)}
                    onCancel={handleEditCancel}
                  />
                ) : (
                  <>
                    <div className="flex justify-between items-start">
                      <div className="flex-1 min-w-0">
                        <MessageFormatter content={parseMessageContent(message.content)} />
                      </div>
                      {message.role === 'user' && (
                        <Button
                          variant="link"
                          size="icon"
                          className="opacity-0 group-hover:opacity-100 transition-opacity ml-2"
                          onClick={() => handleEditStart(message)}
                        >
                          <Pencil className="h-4 w-4" />
                        </Button>
                      )}
                    </div>
                  </>
                )}
              </div>
              
              {message.role === 'assistant' && message.toolInvocations && (
                <div className="mt-4">
                  {message.toolInvocations.map((toolInvocation: any) => {
                    const { toolName, toolCallId, state, args } = toolInvocation;
                    
                    console.log('Tool invocation:', toolInvocation);
                    
                    const status = (() => {
                      switch (state) {
                        case 'partial-call':
                          return 'executing';
                        case 'call':
                          return 'executed';
                        case 'result':
                          return toolInvocation.result?.success === false 
                            ? 'failed' 
                            : 'executed';
                        default:
                          return 'executing';
                      }
                    })();

                    if (toolName === 'getEvents' || toolName === 'getEventsTool') {
                      if (state === 'result' && toolInvocation.result?.success) {
                        return (
                          <EventCardsList 
                            key={toolCallId}
                            events={toolInvocation.result.events}
                            onSendMessage={onSendMessage}
                          />
                        );
                      }
                      
                      if (state === 'partial-call' || state === 'call') {
                        return (
                          <EventCardsList 
                            key={toolCallId}
                            isLoading={true}
                          />
                        );
                      }
                    }
                    
                    if (toolName === 'getEventDetail' || toolName === 'getEventDetailTool') {
                      if (state === 'result' && toolInvocation.result?.success) {
                        return (
                          <div className="max-w-3xl" key={toolCallId}>
                            <EventDetailCard 
                              event={toolInvocation.result.event} 
                              onSendMessage={onSendMessage}
                            />
                          </div>
                        );
                      }
                      
                      if (state === 'partial-call' || state === 'call') {
                        return (
                          <div className="max-w-3xl" key={toolCallId}>
                            <EventDetailCard isLoading />
                          </div>
                        );
                      }
                    }

                    if (toolName === 'createPaymentTool') {
                      if (state === 'result' && toolInvocation.result?.success) {
                        return (
                          <div className="max-w-3xl w-full" key={toolCallId}>
                            <StripeProvider clientSecret={toolInvocation.result.clientSecret}>
                              <PaymentForm />
                            </StripeProvider>
                          </div>
                        );
                      }
                      
                      if (state === 'partial-call' || state === 'call') {
                        return (
                          <Card className="w-full" key={toolCallId}>
                            <CardHeader>
                              <Skeleton className="h-6 w-1/2" />
                            </CardHeader>
                            <CardContent>
                              <Skeleton className="h-40 w-full mb-4" />
                            </CardContent>
                            <CardFooter>
                              <Skeleton className="h-10 w-full" />
                            </CardFooter>
                          </Card>
                        );
                      }
                    }

                    if (toolName === 'generateComponentTool') {
                      if (state === 'result' && toolInvocation.result?.success) {
                        return (
                          <div className="max-w-3xl w-full" key={toolCallId}>
                            <ProgressStates progressStates={toolInvocation.result.progressStates} title={toolInvocation.result.title} />
                          </div>
                        );
                      }
                      
                      if (state === 'partial-call' || state === 'call') {
                        return (
                          <Card className="w-full" key={toolCallId}>
                            <CardHeader>
                              <Skeleton className="h-6 w-1/2" />
                            </CardHeader>
                            <CardContent>
                              <Skeleton className="h-40 w-full mb-4" />
                            </CardContent>
                          </Card>
                        );
                      }
                    }

                    if (toolName === 'createCalendarEventTool') {
                      if (state === 'result' && toolInvocation.result?.success) {
                        return (
                          <div className="max-w-3xl w-full" key={toolCallId}>
                            <CalendarView data={[{
                              day: new Date(toolInvocation.result.event.datetime),
                              events: [{
                                ...toolInvocation.result.event,
                                is_new: true
                              }]
                            }]} />
                          </div>
                        );
                      }
                      
                      if (state === 'partial-call' || state === 'call') {
                        return (
                          <Card className="w-full" key={toolCallId}>
                            <CardHeader>
                              <Skeleton className="h-6 w-1/2" />
                            </CardHeader>
                            <CardContent>
                              <Skeleton className="h-40 w-full mb-4" />
                            </CardContent>
                          </Card>
                        );
                      }
                    }

                    return (
                      <div className="max-w-3xl border rounded-lg p-4" key={toolCallId}>
                        <pre className="text-sm">
                          {JSON.stringify({ toolName, state, result: toolInvocation.result }, null, 2)}
                        </pre>
                      </div>
                    );
                  })}
                </div>
              )}

              {isLastAssistantMessage && !isLoading && !ratedMessageIds.has(message.id) && (
                <div className="flex gap-1 -translate-y-1">
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    className="text-muted-foreground hover:text-foreground h-8 w-8 p-0"
                    onClick={() => handleRate(message.id)}
                  >
                    <ThumbsUp className="h-4 w-4" />
                  </Button>
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    className="text-muted-foreground hover:text-foreground h-8 w-8 p-0"
                    onClick={() => handleRate(message.id)}
                  >
                    <ThumbsDown className="h-4 w-4" />
                  </Button>
                </div>
              )}
            </div>
          </div>
        );
      })}

      {isLoading && messages[messages.length - 1]?.role === 'user' && (
        <div className="flex gap-4">
          <Avatar className="h-8 w-8">
            <AvatarImage src="/agent_avatar.png" />
            <AvatarFallback>A</AvatarFallback>
          </Avatar>
          <div className="flex items-center">
            <span className="text-sm text-muted-foreground">is thinking...</span>
          </div>
        </div>
      )}
    </div>
  )
}
