'use client';

import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Checkbox } from "@/components/ui/checkbox";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Provider } from "../api/types.integrations";
import { useState } from "react";

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
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <img
              src={provider.logo_url || '/default-logo.svg'}
              alt={provider.name}
              className="w-6 h-6 rounded"
            />
            Integration with {provider.name}
          </DialogTitle>
        </DialogHeader>
        
        <div className="flex flex-col gap-6 py-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="flex items-center">
              <h3 className="text-sm font-medium">Choose Permissions</h3>
            </div>
            <div className="flex flex-col gap-4 justify-end">
              {provider.scopes?.map((scope) => (
                <div key={scope.scope} className="flex items-center gap-2">
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
                  <Label htmlFor={scope.scope} className="text-left">
                    {scope.scope_name}
                  </Label>
                </div>
              ))}
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button onClick={handleConfirm} disabled={selectedScopes.length === 0}>
            Continue
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}