'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation';
import { Textarea } from "@/components/ui/textarea"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import { Loader2, AlertCircleIcon } from "lucide-react"
import { 
  Dialog,
  DialogContent, 
  DialogHeader, 
  DialogTitle, 
  DialogDescription,
  DialogFooter
} from "@/components/ui/dialog"
import { submitDeployWaitlistRequest } from "../api/general.api" 
import { toast } from 'sonner';
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Label } from "@/components/ui/label"

interface DeployWaitlistDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export default function DeployWaitlistDialog({ open, onOpenChange }: DeployWaitlistDialogProps) {
    const router = useRouter();
    const [waitlistText, setWaitlistText] = useState("")
    const [useVrx, setUseVrx] = useState(false)
    const [useSse, setUseSse] = useState(false)
    const [isSubmitting, setIsSubmitting] = useState(false)
    const [submissionSent, setSubmissionSent] = useState(false)
    const [error, setError] = useState(false)
    const [textError, setTextError] = useState(false)
    const [typeError, setTypeError] = useState(false)
    
    const resetForm = () => {
      setWaitlistText("");
      setUseVrx(false);
      setUseSse(false);
      setSubmissionSent(false);
      setError(false);
      setTextError(false);
      setTypeError(false);
    }

    const handleSubmit = async () => {
        setIsSubmitting(true)
        setTextError(false)
        setTypeError(false)
        setError(false)

        if (!waitlistText.trim()) {
          setTextError(true)
          setIsSubmitting(false)
          return
        }

        if (!useVrx && !useSse) {
          setTypeError(true)
          setIsSubmitting(false)
          return
        }

        try {
          // Create deployment type string with selected options
          const deployTypes = [];
          if (useVrx) deployTypes.push('vrx');
          if (useSse) deployTypes.push('sse');
          
          await submitDeployWaitlistRequest({
            reason: waitlistText,
            deploy_type: deployTypes.join(',')
          })
          
          toast.success("Request submitted!", {
              description: "Thank you! We'll review your request.",
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

    const handleExploreMcps = () => {
      router.push('/integrations?tab=mcps');
      onOpenChange(false);
    }
  
    return (
      <Dialog open={open} onOpenChange={handleClose}>
        <DialogContent className="sm:max-w-[600px]">
          <DialogHeader>
            <DialogTitle>Due to high demand, we're currently queueing requests:(</DialogTitle>
            <DialogDescription>
              Please tell us briefly why you need it and what you plan to deploy. Waiting time should be less than 1-2 days.
            </DialogDescription>
          </DialogHeader>
          
          <div>
            {textError && (
              <Alert variant="destructive" className="p-4 mb-4">
                <AlertCircleIcon className="h-4 w-4" />
                <AlertTitle className="flex items-center">Please provide some details before submitting</AlertTitle>
              </Alert>
            )}
            {typeError && (
              <Alert variant="destructive" className="p-4 mb-4">
                <AlertCircleIcon className="h-4 w-4" />
                <AlertTitle className="flex items-center">Please select at least one deployment type</AlertTitle>
              </Alert>
            )}
            {error && (
              <Alert variant="destructive" className="p-4 mb-4">
                <AlertCircleIcon className="h-4 w-4" />
                <AlertTitle className="flex items-center">An error occurred. Please try again.</AlertTitle>
              </Alert>
            )}
          </div>
          
          <div className="grid gap-4">
            <Textarea
              placeholder="Describe what you want to deploy and why..."
              className="w-full h-32 bg-background border-border text-foreground placeholder:text-muted-foreground rounded-md"
              value={waitlistText}
              onChange={(e) => {
                setWaitlistText(e.target.value)
                setTextError(false)
              }}
              disabled={submissionSent || isSubmitting}
            />
            
            <div className="space-y-3">
              <Label>How would you like to use deployed MCP?</Label>
              <div className="space-y-2">
                <div className="flex items-center space-x-2">
                  <Checkbox 
                    id="vrx" 
                    checked={useVrx}
                    onCheckedChange={(checked) => {
                      setUseVrx(checked === true);
                      setTypeError(false);
                    }}
                  />
                  <Label htmlFor="vrx" className="cursor-pointer">
                    I want to deploy and use within VeyraX
                  </Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Checkbox 
                    id="sse" 
                    checked={useSse}
                    onCheckedChange={(checked) => {
                      setUseSse(checked === true);
                      setTypeError(false);
                    }}
                  />
                  <Label htmlFor="sse" className="cursor-pointer">
                    I want to deploy and use as a separate /sse endpoint
                  </Label>
                </div>
              </div>
            </div>
          </div>

          <DialogFooter className="flex justify-between sm:justify-end pt-4">
            <Button 
              variant="outline"
              onClick={handleExploreMcps}
              disabled={isSubmitting}
            >
              Explore existing MCPs
            </Button>
            
            <Button 
              onClick={handleSubmit} 
              disabled={isSubmitting || submissionSent}
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Submitting...
                </>
              ) : (
                "Submit Request"
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    )
} 