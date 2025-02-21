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
import { updateMessageAccuracy } from "../../api/api.agent"
import { NotionDatabaseProperties } from "../tools/notion/card-view.notion"

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

export function ChatMessages({ messages, isLoading, onSendMessage, isInitialLoading, chatId }: ChatMessagesProps) {
  
  const [copiedMessageId, setCopiedMessageId] = React.useState<string | null>(null);
  const [ratedMessages, setRatedMessages] = React.useState<Set<string>>(new Set());

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
    <div 
      className="flex flex-col gap-8 p-4 max-w-5xl mx-auto w-full overflow-y-auto"
    >
      {messages.map((message, index) => {
        const showAvatar = index === 0 || messages[index - 1].role !== message.role;
        const isLastAssistantMessage = message.role === 'assistant' && 
          (index === messages.length - 1 || messages[index + 1]?.role === 'user');
        const isLastMessage = index === messages.length - 1;
        console.log(message)
        
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
                                            <NotionPageCardSkeleton />
                                          ) : (
                                            result?.success && (
                                              <NotionPageCard {...result.result} />
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
                                              console.log('Weather data:', result),
                                              <Weather data={result} />
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

                                  case 'notion_getDatabaseProperties':
                                    return (
                                      <ToolWrapper toolName="notion">
                                        <div className="max-w-3xl w-full">
                                          {['partial-call', 'call'].includes(state) ? (
                                            <NotionDatabaseListSkeleton />
                                          ) : (
                                            result?.success && (
                                              <NotionDatabaseProperties database={result.database} />
                                            )
                                          )}
                                        </div>
                                      </ToolWrapper>
                                    );

                                  case 'notion_queryDatabase':
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

                                  case 'notion_updatePage':
                                    return (
                                      <ToolWrapper toolName="notion">
                                        <div className="max-w-3xl w-full">
                                          {['partial-call', 'call'].includes(state) ? (
                                            <NotionPageCardSkeleton />
                                          ) : (
                                            result?.success && (
                                              <NotionPageCard {...result.result} />
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
               !ratedMessages.has(message.id) && (
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