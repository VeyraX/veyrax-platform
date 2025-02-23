"use client"

import { Send } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import { DraftMessageProps } from "./types.outlook"
import { Skeleton } from "@/components/ui/skeleton"

export function DraftMessageCard({ to, subject, body, onSendMessage }: DraftMessageProps & { 
  onSendMessage?: (message: string) => void 
}) {
  const handleSend = () => {
    if (onSendMessage) {
      onSendMessage("Perfect, send it!");
    }
  };

  return (
    <Card className="mb-6 border-t-4 border-t-blue-500">
      <CardContent className="p-4">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">New Message</h2>
          </div>
          <div className="space-y-2">
            <div className="border-b px-0 py-2">{to}</div>
          </div>
          <div className="border-b px-0 py-2">{subject}</div>
          <Separator />
          <div className="min-h-[200px] py-2">{body}</div>
        </div>
      </CardContent>
      <div className="px-4 py-3 bg-muted flex items-center">
        <Button onClick={handleSend}>
          Send
          <Send className="h-4 w-4 ml-2" />
        </Button>
      </div>
    </Card>
  )
}

export function DraftMessageCardSkeleton() {
  return (
    <Card className="mb-6 border-t-4 border-t-blue-500">
      <CardContent className="p-4">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <Skeleton className="h-6 w-32" />
            <Skeleton className="h-8 w-8 rounded-full" />
          </div>
          <div className="space-y-2">
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-4 w-16" />
          </div>
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-[200px] w-full" />
        </div>
      </CardContent>
      <div className="px-4 py-3 bg-muted flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Skeleton className="h-9 w-24" />
          <Skeleton className="h-8 w-8 rounded-full" />
        </div>
        <Skeleton className="h-8 w-20" />
      </div>
    </Card>
  )
}