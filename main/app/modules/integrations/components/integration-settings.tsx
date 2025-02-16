'use client';

import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Checkbox } from "@/components/ui/checkbox";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Provider } from "../api/types.integrations";
import { useState } from "react";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { HelpCircle } from "lucide-react";

interface ScopeDialogProps {
  provider: Provider;
  open: boolean;
  onClose: () => void;
  onConfirm: (scopes: string[], enableIndex: boolean) => void;
}

export function ScopeDialog({ provider, open, onClose, onConfirm }: ScopeDialogProps) {
  const [selectedScopes, setSelectedScopes] = useState<string[]>(
    provider.scopes?.map(scope => scope.scope) || []
  );
  const [enableIndex, setEnableIndex] = useState(false);

  const handleConfirm = () => {
    onConfirm(selectedScopes, enableIndex);
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Configure Integration with {provider.name}</DialogTitle>
        </DialogHeader>
        
        <div className="flex flex-col gap-4 py-4">
          {provider.scopes?.map((scope) => (
            <div key={scope.scope} className="flex items-start space-x-2">
              <Checkbox
                id={scope.scope}
                checked={selectedScopes.includes(scope.scope)}
                onCheckedChange={(checked) => {
                  setSelectedScopes(checked
                    ? [...selectedScopes, scope.scope]
                    : selectedScopes.filter(s => s !== scope.scope)
                  );
                }}
              />
              <div className="grid gap-1.5 leading-none">
                <Label htmlFor={scope.scope}>{scope.scope_name}</Label>
              </div>
            </div>
          ))}

          {provider.has_index_capability && (
            <div className="flex items-start space-x-2 mt-4 pt-4 border-t">
              <Checkbox
                id="enable-index"
                checked={enableIndex}
                onCheckedChange={(checked) => setEnableIndex(checked as boolean)}
              />
              <div className="grid gap-1.5 leading-none">
                <div className="flex items-center gap-2">
                  <Label htmlFor="enable-index">Enable Content Indexing</Label>
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger>
                        <HelpCircle className="h-4 w-4 text-muted-foreground" />
                      </TooltipTrigger>
                      <TooltipContent>
                        <p>We will vectorize your content and you will be able to ask questions about it</p>
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                </div>
              </div>
            </div>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>Cancel</Button>
          <Button onClick={handleConfirm} disabled={selectedScopes.length === 0}>
            Continue
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}