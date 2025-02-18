'use client';

import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Provider, ManageDialogProps } from "../api/types.integrations";
import { disconnectProvider, createProviderIndex, deleteIndexData } from "../api/api.integrantions";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { HelpCircle, RefreshCw } from "lucide-react";
import { Separator } from "@/components/ui/separator";

export function ManageDialog({ provider, open, onClose, onUpdate }: ManageDialogProps) {
  const handleDisconnect = async () => {
    try {
      await disconnectProvider(provider.id);
      onUpdate();
      onClose();
    } catch (error) {
      console.error('Failed to disconnect provider:', error);
    }
  };

  const handleRemoveIndex = async () => {
    try {
      await deleteIndexData(provider.provider_tag);
      onUpdate();
    } catch (error) {
      console.error('Failed to remove index:', error);
    }
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
            {provider.name} Settings
          </DialogTitle>
        </DialogHeader>

        <div className="flex flex-col gap-6 py-4">
          {provider.has_index_capability && (
            <>
              <div className="grid grid-cols-2 gap-4 items-center">
                <div className="flex items-center gap-2">
                  <h3 className="text-sm font-medium leading-none">Index</h3>
                  {provider.hasIndex && (provider.indexStatus === 'synced' || provider.indexStatus === 'failed') && (
                    <RefreshCw 
                      className="h-3 w-3 cursor-pointer text-muted-foreground hover:text-foreground transition-colors"
                      onClick={async () => {
                        try {
                          await deleteIndexData(provider.provider_tag);
                          await createProviderIndex(provider.id, provider.provider_tag);
                          onUpdate();
                        } catch (error) {
                          console.error('Failed to resync index:', error);
                        }
                      }}
                    />
                  )}
                </div>
                {provider.hasIndex ? (
                  <div className="flex flex-col gap-4 items-end">
                    <Badge 
                      variant="secondary"
                      className={
                        provider.indexStatus === 'synced' ? 'bg-green-100 text-green-800' :
                        provider.indexStatus === 'syncing' ? 'bg-blue-100 text-blue-800' :
                        provider.indexStatus === 'failed' ? 'bg-red-100 text-red-800' :
                        provider.indexStatus === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-gray-100 text-gray-800'
                      }
                    >
                      {provider.indexStatus ? provider.indexStatus.charAt(0).toUpperCase() + provider.indexStatus.slice(1) : 'Unknown'}
                    </Badge>
                    {provider.indexStatus !== 'syncing' && (
                      <Badge variant="secondary">
                        {provider.processedEntities || 0} documents
                      </Badge>
                    )}
                  </div>
                ) : (
                  <div className="flex items-center justify-end">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={async () => {
                        try {
                          await createProviderIndex(provider.id, provider.provider_tag);
                          onUpdate();
                        } catch (error) {
                          console.error('Failed to create index:', error);
                        }
                      }}
                    >
                      Create Index
                    </Button>
                  </div>
                )}
              </div>
              <Separator />
            </>
          )}

          {/* OAuth Scopes */}
          {provider.auth_method === 'oauth' && provider.scopes && (
            <div className="grid grid-cols-2 gap-4">
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-medium">Authorized Scopes</h3>
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <HelpCircle className="h-4 w-4 text-muted-foreground" />
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>To change scopes, please disconnect and reconnect with new permissions</p>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
              </div>
              <div className="flex flex-wrap gap-2 justify-end">
                {provider.scopes.map((scope) => (
                  <Badge key={scope.scope} variant="secondary">
                    {scope.scope_name}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </div>

        <DialogFooter className="flex justify-between">
          <div className="flex gap-2">
          {provider.hasIndex && provider.indexStatus !== 'syncing' && (
              <Button
                variant="ghost"
                className="text-red-600 hover:text-red-700 hover:bg-red-50"
                onClick={handleRemoveIndex}
              >
                Remove Index
              </Button>
            )}
            <Button
              variant="destructive"
              onClick={handleDisconnect}
            >
              Disconnect
            </Button>
          </div>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}