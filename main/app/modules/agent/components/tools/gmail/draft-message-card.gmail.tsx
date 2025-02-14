"use client"

import { useState } from "react"
import { Send, Paperclip, MoreVertical } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Separator } from "@/components/ui/separator"
import { DraftMessageProps } from "./types.gmail"
import { Skeleton } from "@/components/ui/skeleton"

export function DraftMessageCard({ to, subject, body, onSendMessage }: DraftMessageProps & { 
  onSendMessage?: (message: string) => void 
}) {
  const [draftData, setDraftData] = useState({ to, subject, body })
  const [showCc, setShowCc] = useState(false)
  const [showBcc, setShowBcc] = useState(false)


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
            <Button variant="ghost" size="icon">
              <MoreVertical className="h-4 w-4" />
            </Button>
          </div>
          <div className="space-y-2">
            <Input
              placeholder="To"
              value={draftData.to}
              onChange={(e) => setDraftData({ ...draftData, to: e.target.value })}
              className="border-0 border-b rounded-none px-0 focus-visible:ring-0"
            />
            {showCc && <Input placeholder="Cc" className="border-0 border-b rounded-none px-0 focus-visible:ring-0" />}
            {showBcc && (
              <Input placeholder="Bcc" className="border-0 border-b rounded-none px-0 focus-visible:ring-0" />
            )}
            <div className="flex items-center space-x-2 text-sm text-muted-foreground">
              <button onClick={() => setShowCc(!showCc)}>Cc</button>
              <button onClick={() => setShowBcc(!showBcc)}>Bcc</button>
            </div>
          </div>
          <Input
            placeholder="Subject"
            value={draftData.subject}
            onChange={(e) => setDraftData({ ...draftData, subject: e.target.value })}
            className="border-0 border-b rounded-none px-0 focus-visible:ring-0"
          />
          <Separator />
          <Textarea
            placeholder="Compose email"
            value={draftData.body}
            onChange={(e) => setDraftData({ ...draftData, body: e.target.value })}
            rows={10}
            className="border-0 resize-none focus-visible:ring-0"
          />
        </div>
      </CardContent>
      <div className="px-4 py-3 bg-muted flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Button onClick={handleSend}>
            Send
            <Send className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="icon">
            <Paperclip className="h-4 w-4" />
          </Button>
        </div>
        <Button variant="ghost" size="sm" onClick={() => console.log("Discard draft")}>
          Discard
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

