import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { McpDeployment } from "../../api/types.integrations.mcp";
import { format, parseISO } from "date-fns";
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Button } from "@/components/ui/button";
import { CheckIcon, CopyIcon } from "lucide-react";
import { useState } from "react";

interface McpDeploymentSheetProps {
  isOpen: boolean;
  onClose: () => void;
  deployment: McpDeployment;
}

export function McpDeploymentSheet({ isOpen, onClose, deployment }: McpDeploymentSheetProps) {
  const [copiedLogs, setCopiedLogs] = useState(false);
  const [copiedError, setCopiedError] = useState(false);
  const [copiedHash, setCopiedHash] = useState(false);

  const handleCopyLogs = () => {
    if (deployment.build_logs) {
      navigator.clipboard.writeText(deployment.build_logs);
      setCopiedLogs(true);
      setTimeout(() => setCopiedLogs(false), 2000);
    }
  };

  const handleCopyError = () => {
    if (deployment.error) {
      navigator.clipboard.writeText(deployment.error);
      setCopiedError(true);
      setTimeout(() => setCopiedError(false), 2000);
    }
  };

  const handleCopyHash = () => {
    if (deployment.commit_hash) {
      navigator.clipboard.writeText(deployment.commit_hash);
      setCopiedHash(true);
      setTimeout(() => setCopiedHash(false), 2000);
    }
  };

  const processBuildLogs = (logs: string): string => {
    if (!logs) return '';
    
    const logsStr = String(logs);
    
    const stepRegex = /^(#\d+)\s+(.*)/; 
    return logsStr
      .split('\\n')
      .map(line => {
        const trimmedLine = line.trim();
        const match = trimmedLine.match(stepRegex);
        if (match) {
          return `${match[1]}\n  ${match[2]}`;
        }
        return trimmedLine; 
      })
      .join('\n');
  };

  const statusColors = {
    pending: 'bg-yellow-100 text-yellow-800',
    building: 'bg-blue-100 text-blue-800',
    success: 'bg-green-100 text-green-800',
    failed: 'bg-red-100 text-red-800',
    ready: 'bg-green-100 text-green-800',
    'in progress': 'bg-blue-100 text-blue-800',
    started: 'bg-yellow-100 text-yellow-800',
  };

  return (
    <Sheet open={isOpen} onOpenChange={onClose}>
      <SheetContent className="sm:max-w-4xl w-[95%] overflow-y-auto">
        <SheetHeader>
          <SheetTitle>Deployment Details</SheetTitle>
        </SheetHeader>
        <div className="mt-6 pb-8 space-y-6">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <h3 className="text-sm font-medium mb-1">Deployment ID</h3>
              <p className="text-sm font-mono">
                {deployment?.deployment_id || `DEP-${typeof deployment?.id === 'string' ? deployment?.id.substring(0, 8) : deployment?.id}`}
              </p>
            </div>
            <div>
              <h3 className="text-sm font-medium mb-1">Status</h3>
              <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${statusColors[deployment?.status] || 'bg-gray-100 text-gray-800'}`}>
                {deployment?.status.charAt(0).toUpperCase() + deployment?.status.slice(1)}
              </span>
            </div>
          </div>
          
          <div className="grid grid-cols-1 gap-4">
            <div>
              <h3 className="text-sm font-medium mb-1">Date</h3>
              <p className="text-sm">
                {deployment?.created_at ? format(parseISO(deployment.created_at), 'PPp') : '-'}
              </p>
            </div>
          </div>

          {deployment?.commit_hash && (
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <h3 className="text-sm font-medium">Commit Hash</h3>
                <Button 
                  onClick={handleCopyHash}
                  size="sm"
                  variant="ghost"
                  className="h-6 w-6"
                >
                  {copiedHash ? <CheckIcon className="h-4 w-4" /> : <CopyIcon className="h-4 w-4" />}
                </Button>
              </div>
              <SyntaxHighlighter 
                language="bash" 
                style={vscDarkPlus}
                customStyle={{ margin: 0, borderRadius: '0.375rem', maxHeight: '400px' }}
              >
                {deployment.commit_hash}
              </SyntaxHighlighter>
            </div>
          )}

          {deployment?.build_logs && (
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <h3 className="text-sm font-medium">Build Logs</h3>
                <Button 
                  onClick={handleCopyLogs}
                  size="sm"
                  variant="ghost"
                  className="h-6 w-6"
                >
                  {copiedLogs ? <CheckIcon className="h-4 w-4" /> : <CopyIcon className="h-4 w-4" />}
                </Button>
              </div>
              <SyntaxHighlighter 
                language="bash" 
                style={vscDarkPlus}
                customStyle={{ margin: 0, borderRadius: '0.375rem', maxHeight: '400px' }}
              >
                {processBuildLogs(deployment.build_logs)}
              </SyntaxHighlighter>
            </div>
          )}

          {deployment?.error && (
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <h3 className="text-sm font-medium">Error</h3>
                <Button 
                  onClick={handleCopyError}
                  size="sm"
                  variant="ghost"
                  className="h-6 w-6"
                >
                  {copiedError ? <CheckIcon className="h-4 w-4" /> : <CopyIcon className="h-4 w-4" />}
                </Button>
              </div>
              <SyntaxHighlighter 
                language="bash" 
                style={vscDarkPlus}
                customStyle={{ margin: 0, borderRadius: '0.375rem', maxHeight: '400px' }}
              >
                {deployment.error}
              </SyntaxHighlighter>
            </div>
          )}
        </div>
      </SheetContent>
    </Sheet>
  );
} 