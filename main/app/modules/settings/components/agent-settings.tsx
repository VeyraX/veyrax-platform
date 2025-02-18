import { Separator } from "@/components/ui/separator"
import { Textarea } from "@/components/ui/textarea"
import { Button } from "@/components/ui/button"
import { useState } from "react"

export default function AgentSettings() {
  const [instructions, setInstructions] = useState("")
  const [isSaving, setIsSaving] = useState(false)

  const handleSaveSettings = async () => {
    setIsSaving(true)
    try {
      // TODO: Add your API call here to save instructions
      await new Promise(resolve => setTimeout(resolve, 1000)) // Temporary simulation
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold tracking-tight">Agent Settings</h2>
        <p className="text-sm text-muted-foreground">
          Customize your agent's behavior and responses.
        </p>
      </div>

      <Separator />

      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Custom Instructions</h3>
        <Textarea
          placeholder="Enter your custom instructions here..."
          className="min-h-[200px]"
          value={instructions}
          onChange={(e) => setInstructions(e.target.value)}
        />
      </div>

      <div className="flex justify-end">
        <Button 
          onClick={handleSaveSettings} 
          disabled={isSaving}
          variant="outline"
        >
          {isSaving ? "Saving..." : "Save changes"}
        </Button>
      </div>
    </div>
  )
}
