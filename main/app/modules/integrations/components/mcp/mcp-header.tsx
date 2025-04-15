import { useState } from "react";
import { ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { McpSettingsDialog } from "./mcp-settings-dialog";

interface McpHeaderProps {
  repoName: string;
  onBack: () => void;
  isAuthor: boolean;
  repoUrl?: string;
}

export function McpHeader({ repoName, onBack, isAuthor, repoUrl }: McpHeaderProps) {
  const [isClaimDialogOpen, setIsClaimDialogOpen] = useState(false);

  return (
    <>
      <div className="flex items-center justify-between w-full px-4 py-2 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800">
        <div className="flex items-center gap-2">
          <button onClick={onBack} className="text-gray-700 dark:text-gray-300 p-1 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800">
            <ArrowLeft size={16} />
          </button>
          <div className="flex items-center text-sm">
            <span className="font-medium text-gray-900 dark:text-gray-100">{repoName}</span>
          </div>
        </div>
        
        {/* Right side of the header */}
        <div className="flex items-center gap-2">
          <Button 
            size="sm"
            variant="outline"
            className="gap-1 rounded-full"
            onClick={() => setIsClaimDialogOpen(true)}
          >
            <span>Is it your MCP? Claim it!</span>
          </Button>
        </div>
      </div>

      <McpSettingsDialog
        open={isClaimDialogOpen}
        onOpenChange={setIsClaimDialogOpen}
        repoName={repoName}
        repoUrl={repoUrl}
      />
    </>
  );
} 