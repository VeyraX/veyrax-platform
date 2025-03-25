import { MessageSquarePlus } from "lucide-react";
import { Button } from "@/components/ui/button";

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
}

export function FlowChatCreateEmptyState({ onSendMessage }: FlowChatCreateEmptyStateProps) {
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
    onSendMessage?.(suggestion.query);
  };

  return (
    <div className="h-full w-full flex items-center justify-center">
      <div className="flex flex-col items-center space-y-8 w-full px-4">
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
      </div>
    </div>
  );
}