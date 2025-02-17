'use client';

import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Provider, ManageDialogProps } from "../api/types.integrations";
import { disconnectProvider, createProviderIndex, deleteIndexData } from "../api/api.integrantions";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { HelpCircle } from "lucide-react";

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
      <DialogContent className="sm:max-w-[425px]">
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

        <div className="flex flex-col gap-4 py-4">
          {/* Connection Status */}
          <div className="flex flex-col gap-2">
            <h3 className="text-sm font-medium">Connection Status</h3>
            <Badge variant="secondary" className="w-fit bg-green-100 text-green-800">
              Connected
            </Badge>
          </div>

          {/* Index Status */}
          {provider.has_index_capability && (
            <div className="flex flex-col gap-2">
              <h3 className="text-sm font-medium">Index Status</h3>
              {provider.hasIndex ? (
                <div className="flex flex-col gap-2">
                  <div className="flex items-center justify-between">
                    <Badge
                      variant="secondary"
                      className={`
                        ${provider.indexStatus === 'syncing' ? 'bg-blue-100 text-blue-800' : ''}
                        ${provider.indexStatus === 'synced' ? 'bg-green-100 text-green-800' : ''}
                        ${provider.indexStatus === 'failed' ? 'bg-red-100 text-red-800' : ''}
                      `}
                    >
                      {provider.indexStatus}
                    </Badge>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-red-600 hover:text-red-700 hover:bg-red-50"
                      onClick={handleRemoveIndex}
                    >
                      Remove Index
                    </Button>
                  </div>
                  {provider.lastSyncDate && (
                    <div className="flex flex-col gap-1">
                      <span className="text-sm text-muted-foreground">
                        Last synced: {new Date(provider.lastSyncDate).toLocaleString()}
                      </span>
                      <span className="text-sm text-muted-foreground">
                        Documents indexed: {provider.processedEntities || 0}
                      </span>
                    </div>
                  )}
                </div>
              ) : (
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">No index created</span>
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
          )}

          {/* OAuth Scopes */}
          {provider.auth_method === 'oauth' && provider.scopes && (
            <div className="flex flex-col gap-2">
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-medium">Authorized Scopes</h3>
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger>
                      <HelpCircle className="h-4 w-4 text-muted-foreground" />
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>To change scopes, please disconnect and reconnect with new permissions</p>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
              </div>
              <div className="flex flex-wrap gap-2">
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
          <Button
            variant="ghost"
            className="text-red-600 hover:text-red-700 hover:bg-red-50"
            onClick={handleDisconnect}
          >
            Disconnect
          </Button>
          <Button variant="outline" onClick={onClose}>
            Close
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}