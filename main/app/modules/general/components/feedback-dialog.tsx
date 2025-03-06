import { useState } from 'react'
import { Textarea } from "@/components/ui/textarea"
import { Button } from "@/components/ui/button"
import { FrownIcon, MehIcon, SmileIcon, Loader2, AlertCircleIcon } from "lucide-react"
import { Toggle } from "@/components/ui/toggle"
import { 
  Dialog,
  DialogContent, 
  DialogHeader, 
  DialogTitle, 
  DialogDescription,
  DialogFooter
} from "@/components/ui/dialog"
import { submitFeedback } from "../api/general.api"
import { toast } from 'sonner';
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"

interface FeedbackDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export default function FeedbackDialog({ open, onOpenChange }: FeedbackDialogProps) {
    const [selectedMood, setSelectedMood] = useState<string>('neutral')
    const [feedbackText, setFeedbackText] = useState("")
    const [isSubmitting, setIsSubmitting] = useState(false)
    const [feedbackSent, setFeedbackSent] = useState(false)
    const [error, setError] = useState(false)
    const [textError, setTextError] = useState(false)
    
    const handleMoodToggle = (mood: string) => {
      setSelectedMood(mood)
    }

    const resetForm = () => {
      setSelectedMood('neutral');
      setFeedbackText("");
      setFeedbackSent(false);
      setError(false);
      setTextError(false);
    }

    const handleSubmit = async () => {
        setIsSubmitting(true)
        setTextError(false)
        setError(false)

        if (!feedbackText.trim()) {
          setTextError(true)
          setIsSubmitting(false)
          return
        }

        try {
          await submitFeedback({
            mood: selectedMood,
            text: feedbackText,
          })
          
          toast.success("Feedback has been submitted!", {
              description: "Thank you for your feedback!",
              action: {
                label: "Hide",
                onClick: () => toast.dismiss(),
              },
            });
          
          resetForm();
          onOpenChange(false);
          
        } catch (error) {
          setError(true)
        } finally {
          setIsSubmitting(false)
        }
    }
    
    const handleClose = () => {
      if (!isSubmitting) {
        onOpenChange(false);
        
        setTimeout(resetForm, 300);
      }
    }
  
    return (
      <Dialog open={open} onOpenChange={handleClose}>
        <DialogContent className="sm:max-w-[600px]">
          <DialogHeader>
            <DialogTitle>Share your Feedback / Ask a Question</DialogTitle>
            <DialogDescription>
              We'd love to hear what you think about our product and help with anything.
            </DialogDescription>
          </DialogHeader>
          
          <div>
            {textError && (
              <Alert variant="destructive" className="p-4 mb-4">
                <AlertCircleIcon className="h-4 w-4" />
                <AlertTitle className="flex items-center">Please provide feedback text before submitting</AlertTitle>
              </Alert>
            )}
            {error && (
              <Alert variant="destructive" className="p-4 mb-4">
                <AlertCircleIcon className="h-4 w-4" />
                <AlertTitle className="flex items-center">An error occurred while submitting your feedback. Please try again.</AlertTitle>
              </Alert>
            )}
          </div>
          
          <div className="grid gap-4 py-2">
            <Textarea
              placeholder="Your feedback / question"
              className="w-full h-32 bg-background border-border text-foreground placeholder:text-muted-foreground rounded-md"
              value={feedbackText}
              onChange={(e) => {
                setFeedbackText(e.target.value)
                setTextError(false)
              }}
              disabled={feedbackSent || isSubmitting}
            />
            
            <div className="flex justify-between items-center">
              <div className="flex items-center space-x-2">
                <Toggle
                  pressed={selectedMood === 'sad'}
                  onPressedChange={() => handleMoodToggle('sad')}
                  className="w-10 h-10 data-[state=on]:bg-muted"
                  disabled={feedbackSent}
                >
                  <FrownIcon className={`w-6 h-6 ${selectedMood === 'sad' ? 'text-red-500 dark:text-red-400' : ''}`} />
                  <span className="sr-only">Sad</span>
                </Toggle>
                <Toggle
                  pressed={selectedMood === 'neutral'}
                  onPressedChange={() => handleMoodToggle('neutral')}
                  className="w-10 h-10 data-[state=on]:bg-muted"
                  disabled={feedbackSent}
                >
                  <MehIcon className={`w-6 h-6 ${selectedMood === 'neutral' ? 'text-yellow-500 dark:text-yellow-400' : ''}`} />
                  <span className="sr-only">Neutral</span>
                </Toggle>
                <Toggle
                  pressed={selectedMood === 'happy'}
                  onPressedChange={() => handleMoodToggle('happy')}
                  className="w-10 h-10 data-[state=on]:bg-muted"
                  disabled={feedbackSent}
                >
                  <SmileIcon className={`w-6 h-6 ${selectedMood === 'happy' ? 'text-green-500 dark:text-green-400' : ''}`} />
                  <span className="sr-only">Happy</span>
                </Toggle>
              </div>
              
              <Button onClick={handleSubmit} disabled={isSubmitting || feedbackSent}>
                {isSubmitting ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  </>
                ) : (
                  "Submit"
                )}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    )
}