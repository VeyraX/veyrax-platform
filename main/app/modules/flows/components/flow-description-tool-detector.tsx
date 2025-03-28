import { useState, useEffect } from 'react';
import { getActionElementsFromHTML, getProviderInfoFromActionElements } from './flow-description-html';

interface Tool {
  provider_id: string;
  provider_name: string;
  logo_url: string;
}

export function useToolsDetector(html: string, actions: any[]) {
  const [usedTools, setUsedTools] = useState<Tool[]>([]);

  useEffect(() => {
    if (!actions.length || !html) return;

    const detectedProviders = new Map<string, Tool>();
    
    const actionElements = getActionElementsFromHTML(html);
    const providersInfo = getProviderInfoFromActionElements(actionElements);
    
    providersInfo.forEach(({ providerName, actionSlug }: { providerName: string; actionSlug: string }) => {
      const matchingAction = actions.find(a => 
        a.provider_name === providerName && a.action_slug === actionSlug
      );
      
      if (matchingAction) {
        detectedProviders.set(matchingAction.provider_id, {
          provider_id: matchingAction.provider_id,
          provider_name: matchingAction.provider_name,
          logo_url: matchingAction.logo_url
        });
      }
    });
    
    setUsedTools(Array.from(detectedProviders.values()));
  }, [html, actions]);

  return { usedTools };
}

export function ToolsList({ tools }: { tools: Tool[] }) {
  return (
    <>
      {tools.length > 0 ? (
        <div className="flex flex-wrap gap-2 p-2 border rounded-md min-h-12 bg-background">
          {tools.map((tool, index) => (
            <div 
              key={`${tool.provider_id}-${index}`}
              className="inline-flex items-center gap-1 bg-white border border-gray-200 rounded-md px-1 py-0.5 shadow-sm"
            >
              <div className="h-3.5 w-3.5 rounded-sm overflow-hidden flex items-center justify-center bg-white">
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