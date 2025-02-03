// components/compact-tool-card.tsx
import { cn } from "@/lib/utils"
import { 
  Card,
  CardHeader,
  CardTitle,
  CardContent,
} from "@/components/ui/card"
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Loader2, CheckCircle2, AlertCircle, ChevronRight, Eye, ChevronDown, Copy, Check, Download } from "lucide-react"
import { Skeleton } from "@/components/ui/skeleton"
import React from "react"
import { toast } from "sonner"

interface ToolInvocationCardProps {
  title: string
  status: 'executing' | 'executed' | 'failed' | 'partial-call' | 'call'
  query?: string
  result?: any
  error?: string
  onView?: () => void
  toolName?: string
  sandboxId?: string | null
}

export function ToolInvocationCard({
  title,
  status,
  query,
  result,
  error,
  onView,
  toolName,
  sandboxId,
}: ToolInvocationCardProps) {
  const [isExpanded, setIsExpanded] = React.useState(false)
  const [copied, setCopied] = React.useState(false)
  const [isDownloading, setIsDownloading] = React.useState(false)
  
  const rowCount = result?.data?.length ?? 0

  const formattedCode = React.useMemo(() => {
    if (toolName === 'pythonTool') {
      return query || '';
    }
    return query || '';
  }, [query, toolName]);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(query || '');
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const hasDownloadableFile = React.useMemo(() => {
    if (!result?.data) return false;
    
    if (typeof result.data === 'string') {
      return result.data.includes('/workspace/');
    }
    
    if (Array.isArray(result.data)) {
      return result.data.some((item: any) => 
        item.text && typeof item.text === 'string' && item.text.includes('/workspace/')
      );
    }
    
    return false;
  }, [result]);

  const getFilePath = () => {
    if (typeof result.data === 'string') {
      return result.data;
    }
    if (Array.isArray(result.data)) {
      const fileItem = result.data.find((item: any) => 
        item.text && typeof item.text === 'string' && item.text.includes('/workspace/')
      );
      return fileItem?.text;
    }
    return null;
  };

  const handleDownload = async () => {
    const filePath = getFilePath();
    if (!filePath || !result.sandboxId) return;

    try {
      setIsDownloading(true);
      const queryParams = new URLSearchParams({
        path: filePath,
        sandboxId: result.sandboxId,
      });
      
      const response = await fetch(`/api/sandbox/download?${queryParams}`);
      
      if (!response.ok) throw new Error('Download failed');
      
      const blob = await response.blob();
      const fileName = filePath.split('/').pop();
      
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = fileName || 'downloaded-file';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Download error:', error);
      toast.error('Failed to download file');
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <div className="w-full">
      <Card className="group hover:shadow-sm transition-shadow text-xs max-w-[1000px]">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 p-3">
          <div className="flex items-center gap-2">
          {status === 'executing' && (
            <Loader2 className="h-4 w-4 text-blue-500 animate-spin" />
          )}
          {status === 'executed' && (
            <CheckCircle2 className="h-4 w-4 text-green-500" />
          )}
          {status === 'failed' && (
            <AlertCircle className="h-4 w-4 text-destructive" />
          )}
          <CardTitle className="text-sm font-medium">{title}</CardTitle>
        </div>
        <div className="flex items-center gap-2">
          <Badge 
            variant={status === 'failed' ? 'destructive' : 'outline'}
            className={cn(
              'text-[0.7rem] px-1.5 py-0.5 capitalize',
              status === 'executed' && 'border-green-200 bg-green-50 text-green-600',
              status === 'executing' && 'bg-blue-50 text-blue-600'
            )}
          >
            {status}
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="p-3 pt-0 space-y-2">
        {(query || status === 'executed') && (
          <div className="space-y-1">
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">
                {toolName === 'pythonTool' 
                  ? 'Python Code'
                  : status === 'executed' && rowCount > 0 
                    ? `Query and results (${rowCount} rows)` 
                    : 'Query'
                }
              </span>
              <Button 
                variant="ghost" 
                size="icon"
                onClick={() => setIsExpanded(!isExpanded)}
                className="h-6 w-6 p-1"
                aria-label={isExpanded ? "Collapse content" : "Expand content"}
              >
                <ChevronDown className={`h-3.5 w-3.5 transition-transform duration-200 ${
                  isExpanded ? "rotate-180" : ""
                }`} />
              </Button>
            </div>

            {isExpanded && (
              <div className="space-y-2 overflow-x-auto">
                {query && (
                  <div className="relative">
                    <pre className={cn(
                      "text-xs p-2 rounded overflow-auto",
                      toolName === 'pythonTool' ? 'bg-[#1e1e1e]' : 'bg-muted/50'
                    )}>
                      <code className={cn(
                        "font-mono whitespace-pre",
                        toolName === 'pythonTool' && "text-white"
                      )}>
                        {formattedCode}
                      </code>
                    </pre>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="absolute top-1 right-1 h-6 w-6 p-1"
                      onClick={handleCopy}
                      aria-label="Copy SQL query"
                    >
                      {copied ? (
                        <Check className="h-3.5 w-3.5" />
                      ) : (
                        <Copy className="h-3.5 w-3.5" />
                      )}
                    </Button>
                  </div>
                )}

                {status === 'executed' && result?.data && (
                  <div className="space-y-2">
                    <div className="overflow-x-auto">
                      {toolName === 'pythonTool' ? (
                        <pre className="text-xs bg-muted/50 p-2 rounded">
                          <code className="font-mono whitespace-pre">
                            {typeof result.data === 'string' 
                              ? result.data 
                              : JSON.stringify(result.data, null, 2)}
                          </code>
                        </pre>
                      ) : null}
                    </div>
                    
                    {hasDownloadableFile && (
                      <div className="flex justify-end">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={handleDownload}
                          disabled={isDownloading}
                          className="h-7 px-2 text-xs"
                        >
                          {isDownloading ? (
                            <Loader2 className="h-3.5 w-3.5 animate-spin mr-1" />
                          ) : (
                            <Download className="h-3.5 w-3.5" />
                          )}
                          Download File
                        </Button>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {status === 'failed' && error && (
          <div className="text-destructive bg-destructive/10 p-1.5 rounded truncate">
            {error}
          </div>
        )}
      </CardContent>
    </Card>
    </div>
  )
}

export function ToolInvocationCardSkeleton() {
  return (
    <Card className="text-xs">
      <CardHeader className="space-y-0 p-3">
        <div className="flex items-center gap-2">
          <Skeleton className="h-4 w-4 rounded-full" />
          <Skeleton className="h-4 w-24" />
        </div>
      </CardHeader>
      <CardContent className="p-3 pt-0 space-y-1">
        <Skeleton className="h-3 w-full" />
        <Skeleton className="h-3 w-3/4" />
      </CardContent>
    </Card>
  )
}