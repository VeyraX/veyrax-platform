'use client';

import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Checkbox } from "@/components/ui/checkbox";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Provider } from "../api/types.integrations";
import { useState } from "react";
import { ShieldAlert, ArrowRight } from "lucide-react";
import Link from "next/link";

interface ScopeDialogProps {
  provider: Provider;
  open: boolean;
  onClose: () => void;
  onConfirm: (scopes: string[]) => void;
}

export function ScopeDialog({ provider, open, onClose, onConfirm }: ScopeDialogProps) {
  const [selectedScopes, setSelectedScopes] = useState<string[]>(
    provider.scopes?.map(scope => scope.scope_name) || []
  );
  const [selectedScopesIds, setSelectedScopesIds] = useState<string[]>(
    provider.scopes?.map(scope => scope.scope_id) || []
  );

  const handleConfirm = () => {
    onConfirm(selectedScopesIds);
  };

  const isGoogleProvider = provider.name.toLowerCase().includes('google') || 
                          provider.name.toLowerCase().includes('gmail') || 
                          provider.name.toLowerCase().includes('drive') || 
                          provider.name.toLowerCase().includes('calendar');

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
        
        {isGoogleProvider && (
          <div className="p-4 border rounded-lg bg-amber-50 border-amber-200 flex gap-3 mb-4">
            <ShieldAlert className="h-5 w-5 text-amber-600 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="text-sm font-semibold mb-1 text-amber-800">Verification in Progress</h3>
              <p className="text-sm text-amber-700">
                Google may show a security warning during connection. This is normal while we complete 
                Google's verification process.
                <br />
                <Button 
                  variant="link" 
                  className="text-amber-800 p-0 h-auto mt-4"
                  asChild
                >
                  <Link 
                    href="/integrations/google-issue" 
                    className="flex items-center gap-1"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    Learn how to proceed
                    <ArrowRight className="h-4 w-4" />
                  </Link>
                </Button>
              </p>
            </div>
          </div>
        )}
        
        <div className="flex flex-col gap-6 py-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="flex items-center">
              <h3 className="text-sm font-medium">Choose Permissions</h3>
            </div>
            <div className="flex flex-col gap-4 justify-end">
              {provider.scopes?.map((scope) => (
                <div key={scope.scope_name} className="flex items-center gap-2">
                  <Checkbox
                    id={scope.scope_name}
                    checked={selectedScopes.includes(scope.scope_name)}
                    onCheckedChange={(checked) => {
                      setSelectedScopes(checked
                        ? [...selectedScopes, scope.scope_name]
                        : selectedScopes.filter(s => s !== scope.scope_name)
                      );
                      setSelectedScopesIds(checked
                        ? [...selectedScopesIds, scope.scope_id]
                        : selectedScopesIds.filter(s => s !== scope.scope_id)
                      );
                    }}
                  />
                  <Label htmlFor={scope.scope_name} className="text-left">
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