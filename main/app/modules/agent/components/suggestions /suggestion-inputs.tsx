import { Button } from "@/components/ui/button"

interface SuggestionInputsProps {
  suggestions: string[]
  onSendMessage: (message: string) => void
  visible?: boolean
}

export function SuggestionInputs({ suggestions, onSendMessage, visible = true }: SuggestionInputsProps) {
  if (!visible || suggestions.length === 0) return null;

  return (
    <div className="flex flex-wrap gap-2 mb-4">
      {suggestions.map((suggestion, index) => (
        <Button
          key={index}
          variant="outline"
          className="rounded-full text-sm px-4 py-2 hover:bg-primary/10"
          onClick={() => onSendMessage(suggestion)}
        >
          {suggestion}
        </Button>
      ))}
    </div>
  )
}