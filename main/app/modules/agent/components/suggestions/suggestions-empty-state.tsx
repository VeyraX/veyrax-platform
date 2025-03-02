import React from "react"
import { Button } from "@/components/ui/button"
import { ArrowRight } from "lucide-react"
import { motion } from "framer-motion"
import { getToolQuestions } from "./suggestions-empty-state-dummy-data"
import { Skeleton } from "@/components/ui/skeleton"
import Link from "next/link"

interface SuggestionsEmptyStateProps {
  onToolClick: (tool: string) => void
  onSelectSuggestion?: (text: string) => void
  connectedTools: { providerTag: string, logoUrl: string, isConnected: boolean }[]
}

function chunk<T>(array: T[], size: number): T[][] {
  const chunked: T[][] = [];
  for (let i = 0; i < array.length; i += size) {
    chunked.push(array.slice(i, i + size));
  }
  return chunked;
}

export function SuggestionsEmptyState({
  onToolClick,
  onSelectSuggestion,
  connectedTools
}: SuggestionsEmptyStateProps) {
  const [selectedTool, setSelectedTool] = React.useState<string | null>(null)
  const containerRef = React.useRef<HTMLDivElement>(null)
  const [toolQuestions, setToolQuestions] = React.useState<any[]>([])
  const [isLoading, setIsLoading] = React.useState(true)

  React.useEffect(() => {
    setIsLoading(true)
    if (!connectedTools || connectedTools.length === 0) {
      setIsLoading(false)
      return
    }
    const trulyConnectedTools = connectedTools
      .filter(tool => tool.isConnected)
      .map(tool => tool.providerTag);
      
    setToolQuestions(getToolQuestions(trulyConnectedTools))
    setIsLoading(false)
  }, [connectedTools])

  React.useEffect(() => {
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setSelectedTool(null)
        setIsLoading(false)
      }
    }

    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setSelectedTool(null)
      }
    }

    document.addEventListener('keydown', handleEscape)
    document.addEventListener('mousedown', handleClickOutside)

    return () => {
      document.removeEventListener('keydown', handleEscape)
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [])

  const handleToolSelect = (tool: string) => {
    setSelectedTool(tool)
  }

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center w-full py-3">
        <p className="text-sm text-muted-foreground mb-4">Not sure what to ask?</p>
        <div className="flex overflow-x-auto gap-4 w-full pb-4 px-4 no-scrollbar justify-center">
          {[1, 2, 3].map((index) => (
            <Skeleton
              key={index}
              className="h-12 w-12 rounded-full flex-shrink-0"
            />
          ))}
        </div>
      </div>
    )
  }

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
            <ArrowRight className="w-4 h-4" />
          </Button>
        </Link>
      </div>
    )
  }

  if (selectedTool) {
    const toolData = toolQuestions.find(tool => tool.toolName === selectedTool)
    if (toolData) {
      return (
        <div 
          ref={containerRef} 
          className="flex flex-col items-start w-full gap-2.5 mt-1"
        >
          {toolData.questions.map((question: string, index: number) => (
            <motion.button
              key={index}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ 
                duration: 0.15,
                delay: index * 0.05,
                ease: [0.16, 1, 0.3, 1]
              }}
              className={`
                text-left text-[15px] text-muted-foreground hover:text-primary hover:bg-muted/50 
                w-full px-3 py-2 rounded-sm transition-colors flex items-center justify-between group
              `}
              onClick={() => {
                onSelectSuggestion?.(question + " ")
              }}
            >
              <span>{question}</span>
              <ArrowRight className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity" />
            </motion.button>
          ))}
        </div>
      )
    }
  }

  return (
    <div className="flex flex-col items-center justify-center w-full py-3">
      <p className="text-sm text-muted-foreground mb-4">Not sure what to ask?</p>
      <div className="flex flex-col gap-1 w-full">
        {chunk(toolQuestions, 7).map((toolGroup, groupIndex) => (
          <div 
            key={groupIndex} 
            className="flex overflow-x-auto gap-4 w-full pb-4 px-4 no-scrollbar justify-center"
          >
            {toolGroup.map((tool) => {
              const connectedTool = connectedTools.find(ct => 
                ct.providerTag === tool.toolName && ct.isConnected
              );
              
              if (!connectedTool) return null;
              
              return (
                <Button
                  key={tool.toolName}
                  variant="outline"
                  size="lg"
                  onClick={() => handleToolSelect(tool.toolName)}
                  className="rounded-full flex-shrink-0 flex items-center justify-center gap-2 px-6 py-3"
                >
                  <img src={connectedTool?.logoUrl || tool.logo} alt={`${tool.toolName} logo`} className="w-6 h-6" />
                </Button>
              );
            })}
          </div>
        ))}
      </div>
    </div>
  )
}