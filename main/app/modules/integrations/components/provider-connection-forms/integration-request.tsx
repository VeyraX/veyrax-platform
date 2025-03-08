import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { upsertIntegrationRequest } from "../../api/api.integrations";
import { AlertCircle, Loader2 } from "lucide-react";
import { toast } from "sonner";

interface IntegrationRequestFormProps {
  onSubmit?: () => void;
  disabled?: boolean;
}

export function IntegrationRequestForm({ onSubmit, disabled = false }: IntegrationRequestFormProps) {
  const [integrationName, setIntegrationName] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!integrationName.trim()) {
      setError("Please enter an integration name");
      return;
    }

    setIsSubmitting(true);
    setError(null);
    
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
      setError("Failed to submit your request. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-4">
      <form onSubmit={handleSubmit}>
        <div className="space-y-4">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded relative flex items-center gap-2" role="alert">
              <AlertCircle className="h-4 w-4" />
              <span className="block sm:inline">{error}</span>
            </div>
          )}

          <div className="space-y-2">
            <Label htmlFor="integrationName">Which integration would you like to see?</Label>
            <Input
              id="integrationName"
              value={integrationName}
              onChange={(e) => setIntegrationName(e.target.value)}
              placeholder="e.g., Salesforce, HubSpot, Asana, etc."
              disabled={disabled || isSubmitting}
            />
          </div>

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
        </div>
      </form>
    </div>
  );
}