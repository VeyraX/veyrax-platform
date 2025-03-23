import { MessageSquarePlus } from "lucide-react";

export function FlowChatCreateEmptyState() {
  return (
    <div className="h-full w-full flex items-center justify-center">
      <div className="flex flex-col items-center space-y-6 max-w-sm text-center px-4">
        <div className="p-4 rounded-full bg-primary/10">
          <MessageSquarePlus className="w-8 h-8 text-primary" />
        </div>
        
        <div className="space-y-2">
          <h3 className="text-xl font-medium">
            Create Your Flow With AI
          </h3>
          <p className="text-muted-foreground text-sm">
            Describe the flow you want to create, and our AI will help you build it step by step.
          </p>
        </div>
      </div>
    </div>
  );
}