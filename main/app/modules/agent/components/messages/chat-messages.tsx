import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { MessageFormatter } from "./message-formatter"
import { Button } from "@/components/ui/button"
import { ThumbsDown, ThumbsUp, Pencil, Copy, Check } from "lucide-react"
import React, { useRef, useEffect } from "react"
import { Skeleton } from "@/components/ui/skeleton"
import { Card, CardHeader, CardContent, CardFooter } from "@/components/ui/card"
import { EditMessage } from "./chat-messages-edit-message"
import { type Message } from 'ai/react'
import { DraftMessageCard } from "../tools/gmail/draft-message-card.gmail"
import { MessageList } from "../tools/gmail/message-list.gmail"
import { DraftMessageCardSkeleton } from "../tools/gmail/draft-message-card.gmail"
import { MessageListSkeleton } from "../tools/gmail/message-list.gmail"
import { MessageCard, MessageCardSkeleton } from "../tools/gmail/message-card.gmail"
import { EventCard, EventCardSkeleton } from "../tools/google-calendar/event-card.google-calendar"
import { Event } from "../tools/google-calendar/types.google-calendar"
import Link from "next/link"
import { FilterDisplay } from "../tools/google-calendar/event-card.google-calendar"
import { ToolWrapper } from "../tools/common/tool-wrapper"
import { NotionDatabaseList, NotionDatabaseListSkeleton } from "../tools/notion/card-view.notion"
import Weather from "../tools/openweather/weather-widget.openweather"
import { PerplexityResponseView, PerplexityResponseSkeleton } from "../tools/perplexity/response-view.perplexity"
import { FileCard, FileCardSkeleton } from "../tools/google-drive/file-card.google-drive"
import { FileList, FileListSkeleton } from "../tools/google-drive/file-list.google-drive"
import { NotionPageCard, NotionPageCardSkeleton } from "../tools/notion/card-view.notion"
import { Page } from "../tools/notion/types.notion"
import { GoogleDriveResponseSkeleton, GoogleDriveResponseView } from "../tools/google-drive/vector-search-view.google-drive"
import { NotionResponseSkeleton, NotionResponseView } from "../tools/notion/vector-search-view.notion"
import { LinearIssueCard, LinearIssueCardSkeleton, LinearProjectList, LinearProjectListSkeleton, LinearTeamList, LinearTeamListSkeleton } from "../tools/linear/card-view.linear"
import { LinearWorkflowStateList, LinearWorkflowStateListSkeleton } from "../tools/linear/card-view.linear"
import { ScrollArea } from "@/components/ui/scroll-area"
import { useAutoScroll } from "@/hooks/use-chat-scroll"

interface ExtendedMessage extends Message {
  image_url?: string;
}

interface ChatMessagesProps {
  messages: ExtendedMessage[]
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
  isInitialLoading?: boolean
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

export function ChatMessages({ messages, messageAttachments, isLoading, sandboxId, onEditMessage, onSendMessage, isInitialLoading }: ChatMessagesProps) {
  const [ratedMessageIds, setRatedMessageIds] = React.useState<Set<string>>(new Set());
  const [editingMessageId, setEditingMessageId] = React.useState<string | null>(null);
  const [copiedMessageId, setCopiedMessageId] = React.useState<string | null>(null);
  
  const { scrollRef, scrollToBottom } = useAutoScroll({
    offset: 20,
    smooth: true,
    content: messages.length
  });

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

  const handleCopy = async (messageId: string, content: string) => {
    await navigator.clipboard.writeText(parseMessageContent(content));
    setCopiedMessageId(messageId);
    setTimeout(() => setCopiedMessageId(null), 2000);
  };

  if (isInitialLoading) {
    return (
      <div 
        className="flex flex-col gap-8 p-4 max-w-5xl mx-auto w-full overflow-y-auto"
      >
        {[1, 2, 3].map((i) => (
          <div 
            key={i} 
            className={`flex gap-4 group ${i % 2 === 0 ? 'justify-end' : ''}`}
          >
            <div className={`grid gap-1.5 ${i % 2 === 0 ? 'max-w-[85%]' : 'w-full'}`}>
              <div className={`${
                i % 2 === 0 
                  ? 'bg-primary text-primary-foreground rounded-xl p-3' 
                  : ''
              } flex-1`}>
                <div className="flex flex-col gap-2">
                  <div className={`h-4 bg-muted animate-pulse rounded ${i % 2 === 0 ? 'w-32' : 'w-48'}`} />
                  <div className={`h-4 bg-muted animate-pulse rounded ${i % 2 === 0 ? 'w-48' : 'w-64'}`} />
                  {i % 2 !== 0 && <div className="h-4 bg-muted animate-pulse rounded w-40" />}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div 
      ref={scrollRef}
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
            className={`flex gap-4 group ${message.role === 'user' ? 'justify-end' : ''}`}
          >
            <div className={`grid gap-1.5 ${
              editingMessageId === message.id 
                ? 'w-full' 
                : message.role === 'user' 
                  ? 'max-w-[75%]'
                  : 'w-full'
            }`}>
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
                  <div className="w-full">
                    <EditMessage
                      content={parseMessageContent(message.content)}
                      onSave={(content: string) => handleEditSave(message.id, content)}
                      onCancel={handleEditCancel}
                    />
                  </div>
                ) : (
                  <>
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
                                      case 'gmail_createDraft':
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

                                      case 'gmail_listMessages':
                                        return (
                                          <ToolWrapper toolName="gmail">
                                            <div className="max-w-3xl w-full space-y-4">
                                              {['partial-call', 'call'].includes(state) ? (
                                                <>
                                                  <MessageListSkeleton />
                                                  <MessageListSkeleton />
                                                  <MessageListSkeleton />
                                                </>
                                              ) : (
                                                result?.messages?.map((message: any, idx: number) => (
                                                  <MessageList
                                                    key={idx}
                                                    {...message}
                                                  />
                                                ))
                                              )}
                                            </div>
                                          </ToolWrapper>
                                        );

                                      case 'gmail_sendMessage':
                                        return (
                                          <ToolWrapper toolName="gmail">
                                            <div className="max-w-3xl w-full">
                                              {['partial-call', 'call'].includes(state) ? (
                                                <MessageCardSkeleton />
                                              ) : (
                                                result?.success && result.message && (
                                                  <MessageCard
                                                    message={result.message}
                                                  />
                                                )
                                              )}
                                            </div>
                                          </ToolWrapper>
                                        );

                                      case 'googleCalendar_createEvent':
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

                                      case 'googleCalendar_listEvents':
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

                                      case 'notion_listDatabases':
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
                                      case 'notion_readPage':
                                        console.log(result)
                                        return (
                                          <ToolWrapper toolName="notion">
                                            <div className="max-w-3xl w-full">
                                              {['partial-call', 'call'].includes(state) ? (
                                                <NotionPageCardSkeleton />
                                              ) : (
                                                result?.success && (
                                                  <NotionPageCard {...result.page} />
                                                )
                                              )}
                                            </div>
                                          </ToolWrapper>
                                        );
                                      case 'notion_searchPages':
                                      case 'notion_listPages':
                                        return (
                                          <ToolWrapper toolName="notion">
                                            <div className="max-w-3xl w-full space-y-4">
                                              {['partial-call', 'call'].includes(state) ? (
                                                <>
                                                  <NotionPageCardSkeleton />
                                                  <NotionPageCardSkeleton />
                                                  <NotionPageCardSkeleton />
                                                </>
                                              ) : (
                                                result?.success && (
                                                  <div className="flex flex-wrap gap-4">
                                                    {result.pages?.map((page: Page) => (
                                                      <NotionPageCard
                                                        key={page.url}
                                                        {...page}
                                                      />
                                                    ))}
                                                  </div>
                                                )
                                              )}
                                            </div>
                                          </ToolWrapper>
                                        );

                                      case 'notion_createPage':
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

                                      case 'openweather_getWeather':
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
                                                    data={toolName === 'openweather_getWeather' 
                                                      ? result.weather 
                                                      : result.forecast} 
                                                  />
                                                )
                                              )}
                                            </div>
                                          </ToolWrapper>
                                        );

                                      case 'perplexity_ask':
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

                                      case 'googleDrive_listFiles':
                                      case 'googleDrive_moveFile':
                                      case 'googleDrive_listFolders':
                                        return (
                                          <ToolWrapper toolName="google-drive">
                                            <div className="max-w-3xl w-full">
                                              {['partial-call', 'call'].includes(state) ? (
                                                <>
                                                  <FileListSkeleton />
                                                  <FileListSkeleton />
                                                  <FileListSkeleton />
                                                </>
                                              ) : (
                                                result?.success && (
                                                  <FileList files={result.files || result.folders} />
                                                )
                                              )}
                                            </div>
                                          </ToolWrapper>
                                        );

                                      case 'googleDrive_getFile':
                                        return (
                                          <ToolWrapper toolName="google-drive">
                                            <div className="max-w-3xl w-full">
                                              {['partial-call', 'call'].includes(state) ? (
                                                <FileCardSkeleton />
                                              ) : (
                                                result?.success && result.file && (
                                                  <FileCard file={result.file} />
                                                )
                                              )}
                                            </div>
                                          </ToolWrapper>
                                        );

                                      case 'googleDrive_readFile':
                                        return (
                                          <ToolWrapper toolName="google-drive">
                                            <div className="max-w-3xl w-full">
                                              {['partial-call', 'call'].includes(state) ? (
                                                <FileCardSkeleton />
                                              ) : (
                                                result?.success && (
                                                  <div className="space-y-4">
                                                    {result.file && <FileCard file={result.file} />}
                                                  </div>
                                                )
                                              )}
                                            </div>
                                          </ToolWrapper>
                                        );

                                      case 'googleDrive_vectorSearch':
                                        return (
                                          <ToolWrapper toolName="google-drive">
                                            <div className="max-w-3xl w-full space-y-4">
                                              {['partial-call', 'call'].includes(state) ? (
                                                <>
                                                  <GoogleDriveResponseSkeleton />
                                                  <GoogleDriveResponseSkeleton />
                                                  <GoogleDriveResponseSkeleton />
                                                </>
                                              ) : (
                                                result?.success && (
                                                  <div className="flex flex-wrap gap-4">
                                                    <GoogleDriveResponseView response={result} />
                                                  </div>
                                                )
                                              )}
                                            </div>
                                          </ToolWrapper>
                                        );

                                      case 'notion_vectorSearch':
                                        return (
                                          <ToolWrapper toolName="notion">
                                            <div className="max-w-3xl w-full space-y-4">
                                              {['partial-call', 'call'].includes(state) ? (
                                                <>
                                                  <NotionResponseSkeleton />
                                                  <NotionResponseSkeleton />
                                                  <NotionResponseSkeleton />
                                                </>
                                              ) : (
                                                result?.success && (
                                                  <div className="flex flex-wrap gap-4">
                                                    <NotionResponseView response={result} />
                                                  </div>
                                                )
                                              )}
                                            </div>
                                          </ToolWrapper>
                                        );

                                      case 'linear_listIssues':
                                      case 'linear_searchIssues':
                                        return (
                                          <ToolWrapper toolName="linear">
                                            <div className="max-w-3xl w-full space-y-4">
                                              {['partial-call', 'call'].includes(state) ? (
                                                <>
                                                  <LinearIssueCardSkeleton />
                                                  <LinearIssueCardSkeleton />
                                                  <LinearIssueCardSkeleton />
                                                </>
                                              ) : (
                                                result?.success && (
                                                  <div className="flex flex-wrap gap-4">
                                                    {result.data?.issues.map((issue: any) => (
                                                      <LinearIssueCard
                                                        key={issue.id}
                                                        {...issue}
                                                      />
                                                    ))}
                                                  </div>
                                                )
                                              )}
                                            </div>
                                          </ToolWrapper>
                                        );
                                      case 'linear_updateIssue':
                                      case 'linear_createIssue':
                                        return (
                                          <ToolWrapper toolName="linear">
                                            <div className="max-w-3xl w-full">
                                              {['partial-call', 'call'].includes(state) ? (
                                                <LinearIssueCardSkeleton />
                                              ) : (
                                                result?.success && result.issue && (
                                                  <LinearIssueCard {...result.issue} />
                                                )
                                              )}
                                            </div>
                                          </ToolWrapper>
                                        );

                                      case 'linear_listProjects':
                                        return (
                                          <ToolWrapper toolName="linear">
                                            <div className="max-w-3xl w-full">
                                              {['partial-call', 'call'].includes(state) ? (
                                                <LinearProjectListSkeleton />
                                              ) : (
                                                result?.success && (
                                                  <LinearProjectList projects={result.data?.projects || []} />
                                                )
                                              )}
                                            </div>
                                          </ToolWrapper>
                                        );

                                      case 'linear_listTeams':
                                        return (
                                          <ToolWrapper toolName="linear">
                                            <div className="max-w-3xl w-full">
                                              {['partial-call', 'call'].includes(state) ? (
                                                <LinearTeamListSkeleton />
                                              ) : (
                                                result?.success && (
                                                  <LinearTeamList teams={result.data?.teams || []} />
                                                )
                                              )}
                                            </div>
                                          </ToolWrapper>
                                        );

                                      case 'linear_listWorkflowStates':
                                        return (
                                          <ToolWrapper toolName="linear">
                                            <div className="max-w-3xl w-full">
                                              {['partial-call', 'call'].includes(state) ? (
                                                <LinearWorkflowStateListSkeleton />
                                              ) : (
                                                result?.success && (
                                                  <LinearWorkflowStateList states={result.data?.states || []} />
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
                          })
                        ) : (
                          <MessageFormatter content={message.content} />
                        )}
                      </div>
                    </div>
                    <div className="flex justify-end gap-2 mt-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      {message.role === 'user' && (
                        <>
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
                        </>
                      )}
                    </div>
                  </>
                )}
              </div>

              {isLastAssistantMessage && !isLoading && !ratedMessageIds.has(message.id) && (
                <div className="flex gap-1 -translate-y-4">
                  <Button 
                    variant="ghost" 
                    size="icon" 
                    className="text-muted-foreground hover:text-foreground h-8 w-8 p-0 rounded-full hover:bg-muted"
                    onClick={() => handleRate(message.id)}
                  >
                    <ThumbsUp className="h-4 w-4" />
                  </Button>
                  <Button 
                    variant="ghost" 
                    size="icon" 
                    className="text-muted-foreground hover:text-foreground h-8 w-8 p-0 rounded-full hover:bg-muted"
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
          <div className="flex items-center">
            <span className="text-sm text-muted-foreground">is thinking...</span>
          </div>
        </div>
      )}
    </div>
  )
}
