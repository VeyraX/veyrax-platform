import React from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"

interface EditMessageProps {
  content: string
  onSave: (content: string) => void
  onCancel: () => void
}

export function EditMessage({ content, onSave, onCancel }: EditMessageProps) {
  const [editContent, setEditContent] = React.useState(content)

  return (
    <div className="flex flex-col gap-2">
      <Textarea
        value={editContent}
        onChange={(e) => setEditContent(e.target.value)}
        className="w-full p-2 border rounded-md"
        rows={3}
        autoFocus
      />
      <div className="flex gap-2">
        <Button
          size="sm"
          variant="link"
          onClick={() => onSave(editContent)}
        >
          Save
        </Button>
        <Button
          size="sm"
          variant="link"
          onClick={onCancel}
        >
          Cancel
        </Button>
      </div>
    </div>
  )
}