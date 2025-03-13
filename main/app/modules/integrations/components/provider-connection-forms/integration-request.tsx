import { useState, useEffect } from "react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { upsertIntegrationRequest } from "../../api/api.integrations";
import { AlertCircle, Loader2 } from "lucide-react";
import { toast } from "sonner";

interface IntegrationRequestFormProps {
  onSubmit?: () => void;
  disabled?: boolean;
  isPublic?: boolean;
}

export function IntegrationRequestForm({ onSubmit, disabled = false, isPublic = false }: IntegrationRequestFormProps) {
  const [integrationName, setIntegrationName] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!integrationName.trim()) {
      return;
    }

    setIsSubmitting(true);
    
    try {
      await upsertIntegrationRequest(integrationName.trim());
      
      toast.success("Request has been submitted!", {
        description: "We'll notify you when it's ready.",
        action: {
          label: "Hide",
          onClick: () => toast.dismiss(),
        },
      });
      
      setIntegrationName("");
      if (onSubmit) onSubmit();
    } catch (err) {
      console.error("Failed to submit integration request:", err);
      toast.error("Failed to submit your request. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-4">
      <form onSubmit={handleSubmit}>
        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="integrationName">Which integration would you like to see?</Label>
            
            {!isPublic ? (
              <Input
                id="integrationName"
                value={integrationName}
                onChange={(e) => setIntegrationName(e.target.value)}
                placeholder="e.g., Salesforce, HubSpot, Asana, etc."
                disabled={disabled || isSubmitting}
              />
            ) : (
              <div className="bg-blue-50 border border-blue-200 text-blue-700 text-sm px-4 py-3 rounded relative" role="alert">
                <p>Please sign in to submit an integration request</p>
              </div>
            )}
          </div>

          {!isPublic ? (
            <Button 
              type="submit" 
              disabled={disabled || isSubmitting || !integrationName.trim()}
              className="w-full"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Submit
                </>
              ) : (
                "Submit"
              )}
            </Button>
          ) : (
            <Button 
              variant="default"
              onClick={() => window.location.href = '/login'}
              className="w-full"
            >
              Sign In
            </Button>
          )}
        </div>
      </form>
    </div>
  );
}