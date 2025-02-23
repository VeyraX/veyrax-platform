"use client"

import { useState } from "react"
import { Mail, ChevronDown, ChevronRight, ExternalLink } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { formatDistanceToNow } from "date-fns"
import { MessageProps } from "./types.outlook"

export function EmailView({ 
  id,
  subject,
  bodyPreview,
  body,
  from_address,
  to_recipients,
  sent_datetime,
  webLink
}: MessageProps) {
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
          <div className="col-span-8 truncate font-medium flex items-center gap-2">
            {subject || 'No Subject'}
            <Button 
              variant="ghost" 
              size="sm" 
              className="h-6 w-6 p-0" 
              onClick={(e) => {
                e.stopPropagation()
                window.open(webLink, '_blank')
              }}
            >
              <ExternalLink className="h-4 w-4" />
            </Button>
          </div>
          <div className="col-span-4 text-right text-sm text-muted-foreground">
            {sent_datetime && formatDistanceToNow(new Date(sent_datetime), { addSuffix: true })}
          </div>
        </div>
      </div>

      {isExpanded && (
        <div className="px-12 py-4 bg-accent/20">
          <div className="space-y-4">
            <div className="flex justify-between text-sm text-muted-foreground">
              <div>From: {from_address || 'Unknown sender'}</div>
              <div>To: {
                Array.isArray(to_recipients) && to_recipients.length > 0 
                  ? to_recipients.join(', ') 
                  : 'No recipients'
              }</div>
              <div>{sent_datetime && new Date(sent_datetime).toLocaleString()}</div>
            </div>
            <div 
              className="whitespace-pre-wrap"
              dangerouslySetInnerHTML={{ __html: body || bodyPreview || 'No content' }}
            />
          </div>
        </div>
      )}
    </div>
  )
}

export function EmailViewSkeleton() {
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