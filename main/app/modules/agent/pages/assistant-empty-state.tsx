import React from "react"
import { AIInputWithSearch } from "../components/input/ai-input"
import { SuggestionsEmptyState } from "../components/suggestions/suggestions-empty-state"
import { ModelId } from "../components/api/models"

interface AssistantEmptyStateProps {
  onSubmit: (message: string, modelId?: ModelId) => Promise<void>
  isLoading: boolean
  onStop: () => void
  userTools: Record<string, any>
  onToolClick: (tool: string) => void
  connectedTools: { providerTag: string, logoUrl: string, isConnected: boolean }[]
  initialInput?: string | null
  availableModels?: string[]
  defaultModelId?: ModelId
  onModelChange?: (modelId: ModelId) => void
}

export function AssistantEmptyState({
  onSubmit,
  isLoading,
  onStop,
  userTools,
  connectedTools,
  onToolClick,
  initialInput,
  availableModels,
  defaultModelId,
  onModelChange
}: AssistantEmptyStateProps) {
  const inputRef = React.useRef<HTMLTextAreaElement>(null)

  const handleSuggestionSelect = (text: string) => {
    if (inputRef.current) {
      const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
        window.HTMLTextAreaElement.prototype,
        'value'
      )?.set
      
      if (nativeInputValueSetter) {
        nativeInputValueSetter.call(inputRef.current, text)
        const event = new Event('input', { bubbles: true })
        inputRef.current.dispatchEvent(event)
      }
      
      inputRef.current.focus()
    }
  }

  return (
    <div className="flex flex-col items-start justify-center h-full max-w-4xl mx-auto px-4 w-full space-y-8">
      <div className="flex flex-col items-start space-y-2">
        <h1 className="text-4xl font-medium text-foreground">
          Welcome to VeyraX.
        </h1>
        <p className="text-xl text-muted-foreground font-normal">
          How can I help you today?
        </p>
      </div>

      <div className="w-full space-y-2">
        <AIInputWithSearch
          ref={inputRef}
          placeholder="What do you want to know?"
          onSubmit={onSubmit}
          className="max-w-none text-lg"
          isLoading={isLoading}
          onStop={onStop}
          userTools={userTools}
          initialInput={initialInput}
          availableModels={availableModels}
          defaultModelId={defaultModelId}
          onModelChange={onModelChange}
        />

        <SuggestionsEmptyState 
          connectedTools={connectedTools}
        />
      </div>
    </div>
  )
}