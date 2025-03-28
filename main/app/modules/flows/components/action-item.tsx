import { Provider } from "@/app/modules/integrations/api/types.integrations";
import { Button } from "@/components/ui/button";
import { X } from "lucide-react";

interface ActionItemProps {
  actionSlug: string;
  logoUrl: string;
  providerName?: string;
  onClick?: (e: React.MouseEvent) => void;
}

export function ActionItem({ actionSlug, logoUrl, providerName, onClick }: ActionItemProps) {
  return (
    <div 
      className="flex items-center gap-2 px-3 py-2 hover:bg-muted cursor-pointer"
      onClick={onClick}
    >
      <div className="h-5 w-5 rounded overflow-hidden flex-shrink-0 flex items-center justify-center bg-white">
        <img 
          src={logoUrl} 
          alt={actionSlug}
          className="max-h-full max-w-full object-contain"
        />
      </div>
      <span className="text-sm">{actionSlug}</span>
      {providerName && (
        <span className="text-xs text-muted-foreground ml-auto">{providerName}</span>
      )}
    </div>
  );
}

export function ActionMention({ actionSlug, logoUrl }: Omit<ActionItemProps, 'onClick'>) {
  return (
    <span className="inline-flex items-center gap-1 bg-white border border-gray-200 rounded-md px-1 py-0.5 text-xs shadow-sm">
      <div className="h-3.5 w-3.5 rounded-sm overflow-hidden flex items-center justify-center bg-white">
        <img 
          src={logoUrl} 
          alt={actionSlug}
          className="max-h-full max-w-full object-contain"
        />
      </div>
      <span className="text-primary font-medium">{actionSlug}</span>
    </span>
  );
}