'use client';

import React from "react"
import { Button } from "@/components/ui/button"
import { Plus } from "lucide-react"
import { useRouter } from "next/navigation"
import Link from "next/link"

interface SuggestionsEmptyStateProps {
  onToolClick: (tool: string) => void
  connectedTools: { providerTag: string, logoUrl: string, isConnected: boolean }[]
}

export function SuggestionsEmptyState({
  onToolClick,
  connectedTools
}: SuggestionsEmptyStateProps) {
  const router = useRouter()

  if (!connectedTools || connectedTools.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center w-full py-3">
        <p className="text-sm text-muted-foreground mb-4">To get started, add actions to your Agent</p>
        <Link href="/integrations">
          <Button
            variant="outline"
            size="lg"
            className="rounded-full flex-shrink-0 flex items-center gap-2"
          >
            Add Actions
          </Button>
        </Link>
      </div>
    )
  }

  return (
    <div className="flex flex-col items-center justify-center w-full py-3">
      <div className="flex flex-col items-center space-y-8 w-full px-4">
        <div className="flex flex-col items-center space-y-4">
          <p className="text-sm text-muted-foreground">Available Tools</p>
          <div className="flex flex-wrap gap-3 justify-center max-w-2xl">
            {connectedTools.filter(tool => tool.isConnected).map((tool) => (
              <div 
                key={tool.providerTag}
                className="flex items-center justify-center w-10 h-10 rounded-full overflow-hidden border border-border bg-white cursor-pointer"
                title={tool.providerTag}
                onClick={() => onToolClick(tool.providerTag)}
              >
                <img 
                  src={tool.logoUrl} 
                  alt={tool.providerTag}
                  className="w-6 h-6 object-contain"
                />
              </div>
            ))}
            <button
              onClick={() => router.push('/integrations')}
              className="flex items-center justify-center w-10 h-10 rounded-full border border-dashed border-border bg-white hover:bg-muted/50 transition-colors"
              title="Add new tool"
            >
              <Plus className="w-4 h-4 text-muted-foreground" />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}