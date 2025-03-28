import { Workflow } from "lucide-react";

export function FlowChatEmptyState() {
  return (
    <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-full">
      <div className="flex flex-col items-center space-y-6 max-w-md mx-auto text-center px-4">
        <div className="p-4 rounded-full bg-primary/10">
          <Workflow className="w-8 h-8 text-primary" />
        </div>
        
        <div className="space-y-2">
          <h3 className="text-xl font-medium">
            Test Your Flow
          </h3>
          <p className="text-muted-foreground text-sm">
            Click the «Test» button or send message here to test your flow.
          </p>
        </div>
      </div>
    </div>
  );
}