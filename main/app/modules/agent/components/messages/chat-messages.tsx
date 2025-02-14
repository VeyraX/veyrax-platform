import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { MessageFormatter } from "./message-formatter"
import { Button } from "@/components/ui/button"
import { ThumbsDown, ThumbsUp, Pencil } from "lucide-react"
import React from "react"
import { Skeleton } from "@/components/ui/skeleton"
import { Card, CardHeader, CardContent, CardFooter } from "@/components/ui/card"
import { useChatScroll } from "@/hooks/use-chat-scroll"
import { EditMessage } from "./chat-messages-edit-message"
import { type Message } from 'ai/react'
import { DraftMessageCard } from "../tools/gmail/draft-message-card.gmail"
import { MessageCard } from "../tools/gmail/message-card.gmail"
import { DraftMessageCardSkeleton } from "../tools/gmail/draft-message-card.gmail"
import { MessageCardSkeleton } from "../tools/gmail/message-card.gmail"
import { SendingMessageCard } from "../tools/gmail/sending-message-card.gmail"
import { EventCard, EventCardSkeleton } from "../tools/calendar/event-card.google-calendar"
import { Event } from "../tools/calendar/types.google-calendar"
import { Table, TableHeader, TableBody, TableCell, TableRow, TableHead } from "@/components/ui/table"
import Link from "next/link"
import { NotionPageList } from "../tools/notion/card-view.notion"
import { FilterDisplay } from "../tools/calendar/event-card.google-calendar"
import { ToolWrapper } from "../tools/tool-wrapper"
import { NotionDatabaseList, NotionDatabaseListSkeleton } from "../tools/notion/card-view.notion"
import { NotionPageListSkeleton } from "../tools/notion/card-view.notion"
import Weather from "../tools/openweather/weather-widget.openweather"
import { type PerplexityResponse } from "../tools/perplexity/types.perplexity"
import { PerplexityResponseView, PerplexityResponseSkeleton } from "../tools/perplexity/response-view.perplexity"


interface ChatMessagesProps {
  messages: Message[]
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
                        {message.parts?.map((part, partIndex) => {
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
                                    case 'createDraftTool':
                                      return (
                                        <ToolWrapper toolName="gmail">
                                          <div className="max-w-3xl w-full">
                                            {['partial-call', 'call'].includes(state) ? (
                                              <DraftMessageCardSkeleton />
                                            ) : (
                                              <DraftMessageCard
                                                to={args.to}
                                                subject={args.subject}
                                                body={args.body}
                                                onSendMessage={onSendMessage}
                                              />
                                            )}
                                          </div>
                                        </ToolWrapper>
                                      );

                                    case 'listMessagesTool':
                                      return (
                                        <ToolWrapper toolName="gmail">
                                          <div className="max-w-3xl w-full space-y-4">
                                            {['partial-call', 'call'].includes(state) ? (
                                              <>
                                                <MessageCardSkeleton />
                                                <MessageCardSkeleton />
                                                <MessageCardSkeleton />
                                              </>
                                            ) : (
                                              result?.messages?.map((message: any, idx: number) => (
                                                <MessageCard
                                                  key={idx}
                                                  {...message}
                                                />
                                              ))
                                            )}
                                          </div>
                                        </ToolWrapper>
                                      );

                                    case 'sendMessageTool':
                                      return (
                                        <ToolWrapper toolName="gmail">
                                          <div className="max-w-3xl w-full">
                                            <SendingMessageCard
                                              state={['partial-call', 'call'].includes(state) ? 'sending' : 
                                                     result?.success ? 'success' : 'error'}
                                            />
                                          </div>
                                        </ToolWrapper>
                                      );

                                    case 'createEventTool':
                                      return (
                                        <ToolWrapper toolName="google-calendar">
                                          <div className="max-w-3xl w-full">
                                            {['partial-call', 'call'].includes(state) ? (
                                              <EventCardSkeleton />
                                            ) : (
                                              result?.success && (
                                                <EventCard {...result.event} />
                                              )
                                            )}
                                          </div>
                                        </ToolWrapper>
                                      );

                                    case 'listEventsTool':
                                      return (
                                        <ToolWrapper toolName="google-calendar">
                                          <div className="max-w-3xl w-full space-y-4">
                                            {['partial-call', 'call'].includes(state) ? (
                                              <>
                                                <EventCardSkeleton />
                                                <EventCardSkeleton />
                                                <EventCardSkeleton />
                                              </>
                                            ) : (
                                              result?.success && (
                                                <>
                                                  {args && <FilterDisplay filters={args} />}
                                                  <div className="flex flex-wrap gap-4">
                                                    {result.events?.map((event: Event) => (
                                                      <EventCard
                                                        key={event.id}
                                                        {...event}
                                                      />
                                                    ))}
                                                  </div>
                                                </>
                                              )
                                            )}
                                          </div>
                                        </ToolWrapper>
                                      );

                                    case 'listDatabasesTool':
                                      return (
                                        <ToolWrapper toolName="notion">
                                          <div className="max-w-3xl w-full space-y-4">
                                            {['partial-call', 'call'].includes(state) ? (
                                              <NotionDatabaseListSkeleton />
                                            ) : (
                                              result?.success && (
                                                <NotionDatabaseList databases={result.databases} />
                                              )
                                            )}
                                          </div>
                                        </ToolWrapper>
                                      );

                                    case 'listPagesTool':
                                      return (
                                        <ToolWrapper toolName="notion">
                                          <div className="max-w-3xl w-full">
                                            {['partial-call', 'call'].includes(state) ? (
                                              <NotionPageListSkeleton />
                                            ) : (
                                              result?.success && (
                                                <NotionPageList pages={result.pages} />
                                              )
                                            )}
                                          </div>
                                        </ToolWrapper>
                                      );

                                    case 'createPageTool':
                                      return (
                                        <ToolWrapper toolName="notion">
                                          <div className="max-w-3xl w-full">
                                            {['partial-call', 'call'].includes(state) ? (
                                              <Card className="w-full max-w-md animate-pulse">
                                                <CardHeader>
                                                  <Skeleton className="h-4 w-3/4" />
                                                </CardHeader>
                                                <CardContent className="space-y-2">
                                                  <Skeleton className="h-4 w-1/2" />
                                                  <Skeleton className="h-4 w-2/3" />
                                                </CardContent>
                                              </Card>
                                            ) : (
                                              result?.success && (
                                                <Card>
                                                  <CardHeader>
                                                    <h3 className="text-lg font-semibold">Page Created Successfully</h3>
                                                  </CardHeader>
                                                  <CardContent>
                                                    <p>Title: {result.page.title}</p>
                                                    <Link 
                                                      href={result.page.url} 
                                                      className="text-blue-600 hover:text-blue-800"
                                                      target="_blank"
                                                    >
                                                      View Page →
                                                    </Link>
                                                  </CardContent>
                                                </Card>
                                              )
                                            )}
                                          </div>
                                        </ToolWrapper>
                                      );

                                    case 'getCurrentWeatherTool':
                                    case 'getWeatherForecastTool':
                                      return (
                                        <ToolWrapper toolName="openweather">
                                          <div className="max-w-3xl w-full">
                                            {['partial-call', 'call'].includes(state) ? (
                                              <Card className="w-full animate-pulse">
                                                <CardContent className="space-y-2">
                                                  <Skeleton className="h-4 w-3/4" />
                                                  <Skeleton className="h-4 w-1/2" />
                                                </CardContent>
                                              </Card>
                                            ) : (
                                              result?.success && (
                                                console.log(result),
                                                <Weather 
                                                  data={toolName === 'getCurrentWeatherTool' 
                                                    ? result.weather 
                                                    : result.forecast} 
                                                />
                                              )
                                            )}
                                          </div>
                                        </ToolWrapper>
                                      );

                                    case 'askPerplexityTool':
                                      return (
                                        <ToolWrapper toolName="perplexity">
                                          <div className="max-w-3xl w-full">
                                            {['partial-call', 'call'].includes(state) ? (
                                              <PerplexityResponseSkeleton />
                                            ) : (
                                              result?.success && result.response && (
                                                <PerplexityResponseView response={result.response} />
                                              )
                                            )}
                                          </div>
                                        </ToolWrapper>
                                      );
                                  }
                                })()}
                              </div>
                            );
                          }
                          return null;
                        })}
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
