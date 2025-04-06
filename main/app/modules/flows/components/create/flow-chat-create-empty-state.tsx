import { MessageSquarePlus, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent } from "@/components/ui/dialog";
import { useState, useEffect } from "react";
import { ProviderAction } from "../../api/types.flows";
import { SimpleIntegrationsList } from "@/app/modules/integrations/components/integration-dialog";

interface SuggestionProps {
  title: string;
  onClick: () => void;
}

function Suggestion({ title, onClick }: SuggestionProps) {
  return (
    <Button
      variant="outline"
      className="rounded-full text-sm px-4 py-2 hover:bg-primary/10"
      onClick={onClick}
    >
      {title}
    </Button>
  );
}

interface FlowChatCreateEmptyStateProps {
  onSendMessage?: (message: string) => void;
  userTools?: ProviderAction[];
  onToolsChange?: () => void;
}

export function FlowChatCreateEmptyState({ 
  onSendMessage, 
  userTools = [],
  onToolsChange
}: FlowChatCreateEmptyStateProps) {
  const [isIntegrationsOpen, setIsIntegrationsOpen] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);
  const [inputValue, setInputValue] = useState("");

  const suggestions = [
    {
      title: "Create Linear tasks from Reddit",
      query: "Create a flow that automatically creates Linear tasks from new Reddit posts matching my search criteria"
    },
    {
      title: "Send GitHub PR reviews to Slack",
      query: "Create a flow that sends notifications to Slack when my GitHub pull requests need review or are approved"
    },
    {
      title: "Save Twitter threads to Notion",
      query: "Create a flow that automatically saves Twitter threads I like to my Notion database"
    },
    {
      title: "Create Linear issues from Discord",
      query: "Create a flow that creates Linear issues from important Discord messages and mentions in specific channels"
    },
    {
      title: "Track GitHub stars in Slack",
      query: "Create a flow that sends Slack notifications when my GitHub repository gets new stars or forks"
    },
    {
      title: "Save Gmail to Notion",
      query: "Create a flow that saves important Gmail emails to my Notion workspace automatically"
    }
  ];

  const handleSuggestionClick = (suggestion: typeof suggestions[0]) => {
    setInputValue(suggestion.query);
    const event = new CustomEvent('inputValueChange', { 
      detail: { value: suggestion.query } 
    });
    window.dispatchEvent(event);
  };

  const handleIntegrationChange = () => {
    setIsIntegrationsOpen(false);
    onToolsChange?.();
    setRefreshKey(prev => prev + 1);
  };

  useEffect(() => {
    const handleSubmit = () => {
      if (inputValue) {
        onSendMessage?.(inputValue);
        setInputValue("");
      }
    };

    window.addEventListener('submitInputValue', handleSubmit);
    return () => {
      window.removeEventListener('submitInputValue', handleSubmit);
    };
  }, [inputValue, onSendMessage]);

  return (
    <div className="h-full w-full flex items-center justify-center">
      <div className="flex flex-col items-center space-y-8 w-full px-4">
        <div className="flex flex-col items-center space-y-4" key={refreshKey}>
          <div className="flex flex-wrap gap-3 justify-center max-w-2xl">
            {userTools.length > 0 && Array.from(new Set(userTools.map(t => t.provider_id))).map(providerId => {
              const tool = userTools.find(t => t.provider_id === providerId);
              return (
                <div 
                  key={providerId}
                  className="flex items-center justify-center w-10 h-10 rounded-full overflow-hidden border border-border bg-white"
                  title={tool?.provider_name}
                >
                  <img 
                    src={tool?.logo_url} 
                    alt={tool?.provider_name}
                    className="w-6 h-6 object-contain"
                  />
                </div>
              );
            })}
            <button
              onClick={() => setIsIntegrationsOpen(true)}
              className="flex items-center justify-center w-10 h-10 rounded-full border border-dashed border-border bg-white hover:bg-muted/50 transition-colors"
              title="Add new tool"
            >
              <Plus className="w-4 h-4 text-muted-foreground" />
            </button>
          </div>
        </div>

        <div className="flex flex-col items-center space-y-6 text-center">
          <h3 className="text-xl font-medium">
            What flow do you want to create?
          </h3>
        </div>

        <div className="flex flex-wrap gap-2 justify-center max-w-2xl">
          {suggestions.map((suggestion, index) => (
            <Suggestion
              key={index}
              title={suggestion.title}
              onClick={() => handleSuggestionClick(suggestion)}
            />
          ))}
        </div>

        <Dialog open={isIntegrationsOpen} onOpenChange={setIsIntegrationsOpen}>
          <DialogContent className="max-w-3xl h-[600px] overflow-hidden p-0">
            <SimpleIntegrationsList 
              onClose={handleIntegrationChange} 
              return_url={window.location.pathname}
            />
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
}