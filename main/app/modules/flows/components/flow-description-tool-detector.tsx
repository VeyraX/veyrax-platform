import { useState, useEffect } from 'react';
import { getActionElementsFromHTML, getProviderInfoFromActionElements } from './flow-description-html';
import { Alert, AlertDescription } from "@/components/ui/alert";
import { ExclamationTriangleIcon } from "@radix-ui/react-icons";

interface Tool {
  provider_id: string;
  provider_name: string;
  logo_url: string;
}

export function useToolsDetector(html: string, actions: any[]) {
  const [usedTools, setUsedTools] = useState<Tool[]>([]);
  const [missingTools, setMissingTools] = useState<{providerName: string; actionSlug: string}[]>([]);

  useEffect(() => {
    if (!actions.length || !html) {
      setUsedTools([]);
      setMissingTools([]);
      return;
    }

    const detectedProviders = new Map<string, Tool>();
    const missing: {providerName: string; actionSlug: string}[] = [];
    
    const actionElements = getActionElementsFromHTML(html);
    const providersInfo = getProviderInfoFromActionElements(actionElements);
    
    providersInfo.forEach(({ providerName, actionSlug }: { providerName: string; actionSlug: string }) => {
      // Нормализация имени провайдера для сравнения
      const normalizedProviderName = providerName.toLowerCase().trim();
      const normalizedActionSlug = actionSlug.trim();
      
      
      const matchingAction = actions.find(a => 
        a.provider_name.toLowerCase().trim() === normalizedProviderName && 
        a.action_slug === normalizedActionSlug
      );
      
      if (matchingAction) {
        detectedProviders.set(matchingAction.provider_id, {
          provider_id: matchingAction.provider_id,
          provider_name: matchingAction.provider_name,
          logo_url: matchingAction.logo_url
        });
      } else {
        // Add to missing tools if user doesn't have this tool
        missing.push({ providerName: normalizedProviderName, actionSlug: normalizedActionSlug });
      }
    });
    
    const usedToolValues = Array.from(detectedProviders.values());
    
    setUsedTools(usedToolValues);
    setMissingTools(missing);
  }, [html, actions]);

  return { usedTools, missingTools };
}

export function ToolsList({ tools }: { tools: Tool[] }) {
  return (
    <>
      {tools.length > 0 ? (
        <div className="flex flex-wrap gap-2 p-2 border rounded-md min-h-12 bg-background">
          {tools.map((tool, index) => (
            <div 
              key={`${tool.provider_id}-${index}`}
              className="inline-flex items-center gap-1 bg-background border border-gray-200 dark:border-gray-700 rounded-md px-1 py-0.5 shadow-sm"
            >
              <div className="h-3.5 w-3.5 rounded-sm overflow-hidden flex items-center justify-center bg-white dark:bg-gray-800">
                <img 
                  src={tool.logo_url} 
                  alt={tool.provider_name}
                  className="max-h-full max-w-full object-contain"
                />
              </div>
              <span className="text-primary text-xs font-medium">{tool.provider_name}</span>
            </div>
          ))}
        </div>
      ) : (
        <div className="flex items-center justify-center p-4 border rounded-md bg-background text-muted-foreground text-sm min-h-12">
          No tools used yet. Mention actions with @ in your description.
        </div>
      )}
    </>
  );
}

export function MissingToolsAlert({ 
  missingTools, 
  onConnectClick 
}: { 
  missingTools: {providerName: string; actionSlug: string}[];
  onConnectClick?: () => void;
}) {
  if (missingTools.length === 0) return null;
  
  // Group by provider name to avoid duplicates
  const uniqueProviders = Array.from(new Set(missingTools.map(t => t.providerName)));

  return (
    <Alert variant="default" className="mb-4 border-yellow-500 bg-yellow-50 dark:bg-yellow-900/20 text-yellow-800 dark:text-yellow-300">
      <div className="flex items-center">
        <AlertDescription className="flex items-center justify-between w-full">
          <span>
            {uniqueProviders.length === 1 
              ? `${uniqueProviders[0]} tool used in description is not connected.` 
              : `${uniqueProviders.join(', ')} tools used in description are not connected.`}
          </span>
          <button 
            onClick={onConnectClick}
            className="text-sm font-medium underline text-yellow-800 dark:text-yellow-300 hover:text-yellow-900 dark:hover:text-yellow-200 ml-2 flex-shrink-0"
          >
            Connect now
          </button>
        </AlertDescription>
      </div>
    </Alert>
  );
}