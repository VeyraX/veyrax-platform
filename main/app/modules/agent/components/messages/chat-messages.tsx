import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { MessageFormatter } from "./message-formatter"
import { ToolInvocationCard } from "../tools/tool-invocation-card"
import { Button } from "@/components/ui/button"
import { ThumbsDown, ThumbsUp, Pencil } from "lucide-react"
import React from "react"
import { Textarea } from "@/components/ui/textarea"
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
}

function parseMessageContent(content: string) {
  const tableMarker = "\n\nTable content:";
  const textMarker = "\n\nText content:";
  const fileMarker = "\n\nFile Information:";
  
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
  
  return cleanContent;
}

export function ChatMessages({ messages, messageAttachments, isLoading, sandboxId, onEditMessage }: ChatMessagesProps) {
  const [ratedMessageIds, setRatedMessageIds] = React.useState<Set<string>>(new Set());
  const [editingMessageId, setEditingMessageId] = React.useState<string | null>(null);
  const [editContent, setEditContent] = React.useState<string>("");

  const handleRate = (messageId: string) => {
    setRatedMessageIds(prev => new Set(prev).add(messageId));
  };

  const handleEditStart = (message: any) => {
    setEditingMessageId(message.id);
    setEditContent(parseMessageContent(message.content));
  };

  const handleEditSave = async (messageId: string) => {
    await onEditMessage?.(messageId, editContent);
    setEditingMessageId(null);
    setEditContent("");
  };

  const handleEditCancel = () => {
    setEditingMessageId(null);
    setEditContent("");
  };

  return (
    <div className="flex flex-col gap-8 p-4 max-w-5xl mx-auto w-full">
      {messages.map((message, index) => {
        const showAvatar = index === 0 || messages[index - 1].role !== message.role;
        const currentAttachments = messageAttachments[message.id];
        const isLastAssistantMessage = message.role === 'assistant' && 
          (index === messages.length - 1 || messages[index + 1]?.role === 'user');
        
        return (
          <div key={message.id} className="flex gap-4 group">
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
                  <div className="flex flex-col gap-2">
                    <Textarea
                      value={editContent}
                      onChange={(e) => setEditContent(e.target.value)}
                      className="w-full p-2 border rounded-md"
                      rows={3}
                      autoFocus
                    />
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="link"
                        onClick={() => handleEditSave(message.id)}
                      >
                        Save
                      </Button>
                      <Button
                        size="sm"
                        variant="link"
                        onClick={handleEditCancel}
                      >
                        Cancel
                      </Button>
                    </div>
                  </div>
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

                    if (toolName === 'pythonTool') {
                      return (
                        <div className="w-[900px]">
                          <ToolInvocationCard
                            key={toolCallId}
                            title="Python Code Execution"
                            status={status}
                            query={args?.code}
                            error={state === 'result' ? toolInvocation.result?.error : undefined}
                            result={state === 'result' ? toolInvocation.result : undefined}
                            toolName={toolName}
                            sandboxId={sandboxId}
                          />
                        </div>
                      );
                    }

                    return (
                      <div className="w-[900px]">
                        <ToolInvocationCard
                          key={toolCallId}
                          toolName={toolName}
                          title="Tool Execution"
                          status={status}
                          query={args?.query}
                          error={state === 'result' ? toolInvocation.result?.error : undefined}
                          result={state === 'result' ? toolInvocation.result : undefined}
                        />
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
