import { Mail, ChevronDown, ChevronRight } from "lucide-react"
import { Card } from "@/components/ui/card"
import { MessageProps } from "./types.gmail"
import { Skeleton } from "@/components/ui/skeleton"
import { Button } from "@/components/ui/button"
import { formatDistanceToNow } from "date-fns"
import { useState } from "react"

export function MessageCard({ subject, snippet, body, sender, recipient, labels = [], date }: MessageProps) {
  const [isExpanded, setIsExpanded] = useState(false)

  return (
    <div className="border-b border-border hover:shadow-sm transition-shadow">
      <div 
        className="flex items-center px-4 py-2 cursor-pointer hover:bg-accent/50"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <Button 
          variant="ghost" 
          size="sm" 
          className="h-6 w-6 p-0 mr-2" 
          onClick={(e) => {
            e.stopPropagation()
            setIsExpanded(!isExpanded)
          }}
        >
          {isExpanded ? (
            <ChevronDown className="h-4 w-4" />
          ) : (
            <ChevronRight className="h-4 w-4" />
          )}
        </Button>
        
        <div className="flex-1 grid grid-cols-12 gap-4 items-center min-w-0">
          <div className="col-span-9 truncate font-medium">{subject}</div>
          <div className="col-span-3 text-right text-sm text-muted-foreground">
            {formatDistanceToNow(new Date(date), { addSuffix: true })}
          </div>
        </div>
      </div>

      {isExpanded && (
        <div className="px-12 py-4 bg-accent/20">
          <div className="space-y-4">
            <div className="flex justify-between text-sm text-muted-foreground">
              <div>From: {sender}</div>
              <div>{new Date(date).toLocaleString()}</div>
            </div>
            <div className="whitespace-pre-wrap">{body}</div>
          </div>
        </div>
      )}
    </div>
  )
}

export function MessageCardSkeleton() {
  return (
    <div className="border-b border-border px-4 py-2">
      <div className="flex items-center">
        <Skeleton className="h-4 w-4 mr-2" />
        <div className="flex-1 grid grid-cols-12 gap-4">
          <div className="col-span-9">
            <Skeleton className="h-4 w-48" />
          </div>
          <div className="col-span-3">
            <Skeleton className="h-4 w-24 ml-auto" />
          </div>
        </div>
      </div>
    </div>
  )
}

