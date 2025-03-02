"use client"

import { useState, useEffect } from "react"
import { Send, Check, X } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import { cn } from "@/lib/utils"

interface SendingMessageCardProps {
  state: 'sending' | 'success' | 'error'
}

export function SendingMessageCard({ state }: SendingMessageCardProps) {
  const [animation, setAnimation] = useState(false)

  useEffect(() => {
    setAnimation(true)
  }, [])

  return (
    <Card className={cn(
      "mb-6 border-t-4 transition-all duration-500 transform",
      animation ? "translate-y-0 opacity-100" : "translate-y-4 opacity-0",
      state === 'sending' && "border-t-yellow-500",
      state === 'success' && "border-t-green-500",
      state === 'error' && "border-t-red-500"
    )}>
      <CardContent className="p-4">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">
              {state === 'sending' && "Sending Message"}
              {state === 'success' && "Message Sent"}
              {state === 'error' && "Failed to Send"}
            </h2>
            <div className="flex items-center">
              {state === 'sending' && (
                <Send className="h-5 w-5 text-yellow-500 animate-pulse" />
              )}
              {state === 'success' && (
                <Check className="h-5 w-5 text-green-500" />
              )}
              {state === 'error' && (
                <X className="h-5 w-5 text-red-500" />
              )}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}