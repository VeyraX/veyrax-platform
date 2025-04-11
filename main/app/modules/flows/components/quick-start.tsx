import { useState } from "react";
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { CheckIcon, CopyIcon, ExternalLink } from "lucide-react";

interface QuickStartProps {
  flowName?: string;
  isOwner?: boolean;
  isAuthenticated?: boolean;
}

export function QuickStart({ flowName = "", isOwner = false, isAuthenticated = false }: QuickStartProps) {
  const [copied, setCopied] = useState(false);
  const commandText = `Run «${flowName}» flow via VeyraX.`;

  return (
    <div className="bg-white dark:bg-gray-900 rounded-md border border-gray-200 dark:border-gray-800 p-6 space-y-4">
      <h2 className="text-xl font-medium text-foreground">Quick Start</h2>
      <div className="text-sm text-muted-foreground space-y-3">
        <p>
          This flow is designed to run by AI agents. You can execute it through any system 
          where these AI agents can make calls to Veyrax using our <a href="https://docs.veyrax.com/api" 
          className="text-gray-900 dark:text-gray-100 inline-flex items-center gap-1 hover:underline">
            API toolkit
            <ExternalLink className="h-2.5 w-2.5" />
          </a>.
        </p>
        <p>
          Common ways to run this flow via <a href="https://cursor.sh" 
          className="text-gray-900 dark:text-gray-100 inline-flex items-center gap-1 hover:underline">
            Cursor / Windsurf / Cline / Claude
            <ExternalLink className="h-2.5 w-2.5" />
          </a> or any other MCP compatible environment.
        </p>
        {(!isAuthenticated || !isOwner) && (
          <p className="text-muted-foreground">
            To clone this flow and implement it in your own environment, simply click the Clone button in the header. 
            Before using the cloned flow, make sure you have all the required tools enabled in your account.
          </p>
        )}
        <p>
          To get it running, just ask Agent to run the flow:
        </p>
        <div className="relative">
          <div className="absolute right-3 top-1/2 -translate-y-1/2">
            <button
              onClick={() => {
                navigator.clipboard.writeText(commandText);
                setCopied(true);
                setTimeout(() => setCopied(false), 2000);
              }}
              className="h-6 w-6 p-0 flex items-center justify-center text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300"
            >
              {copied ? <CheckIcon className="h-4 w-4" /> : <CopyIcon className="h-4 w-4" />}
            </button>
          </div>
          <SyntaxHighlighter
            language="bash"
            style={vscDarkPlus}
            customStyle={{ margin: 0, borderRadius: '0.375rem', paddingRight: '2.5rem' }}
          >
            {commandText}
          </SyntaxHighlighter>
        </div>
      </div>
    </div>
  );
} 