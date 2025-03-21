'use client'

import { FC, useState } from 'react'
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ArrowUpRight, Plus, Files, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { IntegrationCardProps } from '../api/types.integrations'
import { useRouter } from 'next/navigation'
import { ScopeDialog } from './integration-settings'
import { Provider } from '../api/types.integrations'
import { initiateOAuthFlow, enableProvider } from '../api/api.integrations'
import { ManageDialog } from './integration-manage'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { IntegrationRequestForm } from './provider-connection-forms/integration-request'

export const IntegrationCard: FC<IntegrationCardProps & { isPublic?: boolean }> = (props) => {
  const router = useRouter()
  const [showSettings, setShowSettings] = useState(false);
  const [showManage, setShowManage] = useState(false);
  const [showRequestForm, setShowRequestForm] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const { isPublic = false } = props;
  
  const isRequestCard = props.provider_tag === 'integration-request';

  const handleShowSettings = (provider: Provider) => {
    setShowSettings(true);
  };

  const handleSettingsClose = () => {
    setShowSettings(false);
  };

  const handleSettingsConfirm = async (scopes: string[]) => {
    setShowSettings(false);
    try {
      const url = await initiateOAuthFlow(props.provider_tag, scopes);
      window.location.href = url;
    } catch (error) {
      console.error(`Failed to start OAuth flow for ${props.name}:`, error);
    }
  };

  const handleConnect = async () => {
    if (isRequestCard) {
      setShowRequestForm(true);
      return;
    }
    
    if (props.provider_tag && props.provider_tag.toLowerCase() === 'veyrax') {
      if (!props.connected) {
        setIsConnecting(true);
        try {
          await enableProvider(props.id);
          if (props.onConnectionChange) {
            props.onConnectionChange();
          }
        } catch (error) {
          console.error(`Failed to connect ${props.name}:`, error);
        } finally {
          setIsConnecting(false);
        }
      } else {
        setShowManage(true);
      }
      return;
    }
    
    if (props.auth_method === 'api_key' || props.auth_method === 'api_key_with_base' || props.auth_method === 'db_access') {
      setShowManage(true);
    } else if (props.auth_method === 'none') {
      setIsConnecting(true);
      try {
        await enableProvider(props.id);
        if (props.onConnectionChange) {
          props.onConnectionChange();
        }
      } catch (error) {
        console.error(`Failed to connect ${props.name}:`, error);
      } finally {
        setIsConnecting(false);
      }
    } else {
      handleShowSettings(props as Provider);
    }
  };
  
  const handleDocsClick = () => {
    if (isPublic) {
      router.push(`/marketplace/${props.provider_tag}`);
    } else {
      router.push(`/integrations/${props.provider_tag}`);
    }
  };
  
  const handleRequestFormSubmit = () => {
    setShowRequestForm(false);
    if (props.onConnectionChange) {
      props.onConnectionChange();
    }
  };
  
  return (
    <>
      <Card 
        className={`w-full shadow-none rounded-lg h-[204px] ${
          isRequestCard 
            ? "border-2 border-dashed border-primary" 
            : "border"
        }`}
      >
        <CardContent className="p-4 h-full flex flex-col">
          <div className="flex flex-col gap-3 flex-1">
            <div className="flex justify-between items-center">
              <img 
                src={props.logo_url || '/default-logo.svg'} 
                alt={props.name} 
                width={36} 
                height={36} 
                className="rounded-lg object-contain w-[36px] h-[36px] p-[3px]"
                onError={(e) => {
                  e.currentTarget.src = '/default-logo.svg'
                }}
              />
              {!isPublic && props.connected && (
                <Badge variant="secondary" className="bg-green-50 text-green-700 dark:bg-green-900/30 dark:text-green-300 transition-colors text-xs">
                  Connected
                </Badge>
              )}
            </div>
            <div className="flex-1 min-w-0">
              <h2 className="text-base md:text-lg font-semibold truncate">{props.name}</h2>
              <p className="text-muted-foreground mt-1 text-xs sm:text-sm line-clamp-2">{props.description}</p>
            </div>
          </div>

          <div className="flex items-center mt-3 pt-3 justify-between gap-2">
            {!isRequestCard && (
              <Button
                variant="outline"
                size="sm"
                onClick={handleDocsClick}
                className="text-xs"
              >
                Docs
                <Files className="h-3 w-3 ml-1" />
              </Button>
            )}
            
            {isRequestCard ? (
              <Button 
                variant="outline"
                size="sm"
                onClick={handleConnect}
                className="ml-auto text-xs"
              >
                Request
                <Plus className="h-3 w-3 ml-1" />
              </Button>
            ) : !isPublic && (
              props.connected ? (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowManage(true)}
                  className="text-xs"
                >
                  Manage
                  <ArrowUpRight className="h-3 w-3 ml-1" />
                </Button>
              ) : (
                <Button 
                  variant="outline"
                  size="sm"
                  onClick={handleConnect}
                  disabled={isConnecting}
                  className="text-xs"
                >
                  {isConnecting ? (
                    <Loader2 className="h-3 w-3 animate-spin" />
                  ) : (
                    <>
                      Connect
                      <Plus className="h-3 w-3 ml-1" />
                    </>
                  )}
                </Button>
              )
            )}
          </div>
        </CardContent>
      </Card>

      <Dialog open={showRequestForm} onOpenChange={setShowRequestForm}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <img
                src={props.logo_url || '/default-logo.svg'}
                alt={props.name}
                className="w-6 h-6 rounded"
              />
              Request Integration
            </DialogTitle>
          </DialogHeader>
          <IntegrationRequestForm 
            onSubmit={handleRequestFormSubmit}
            isPublic={isPublic}
          />
        </DialogContent>
      </Dialog>

      {!isPublic && (
        (props.auth_method === 'api_key' || 
         props.auth_method === 'api_key_with_base' ||
         props.auth_method === 'db_access' || 
         (props.provider_tag && props.provider_tag.toLowerCase() === 'veyrax') ||
         (props.auth_method === 'none' && props.connected)) && (
          <ManageDialog
            provider={props}
            open={showManage}
            onClose={() => setShowManage(false)}
            onUpdate={props.onConnectionChange || (() => {})}
          />
        )
      )}
      
      {!isPublic && props.auth_method === 'oauth' && props.connected && (
        <ManageDialog
          provider={props}
          open={showManage}
          onClose={() => setShowManage(false)}
          onUpdate={props.onConnectionChange || (() => {})}
        />
      )}

      {!isPublic && props.auth_method === 'oauth' && (
        <ScopeDialog
          provider={{
            id: props.id,
            name: props.name,
            description: props.description,
            logo_url: props.logo_url,
            provider_tag: props.provider_tag,
            auth_method: props.auth_method as 'oauth' | 'api_key',
            scopes: props.scopes,
          }}
          open={showSettings}
          onClose={handleSettingsClose}
          onConfirm={handleSettingsConfirm}
        />
      )}
    </>
  )
}