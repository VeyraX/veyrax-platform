'use client'

import { FC, useState } from 'react'
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ArrowUpRight, Plus, Files } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { IntegrationCardProps } from '../api/types.integrations'
import { useRouter } from 'next/navigation'
import { ScopeDialog } from './integration-settings'
import { Provider } from '../api/types.integrations'
import { disconnectProvider, initiateOAuthFlow, enableApiKeyProvider } from '../api/api.integrations'
import { ManageDialog } from './integration-manage'

export const IntegrationCard: FC<IntegrationCardProps & { isPublic?: boolean }> = (props) => {
  const router = useRouter()
  const [showSettings, setShowSettings] = useState(false);
  const [showManage, setShowManage] = useState(false);
  const { isPublic = false } = props;

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

  const handleConnect = () => {
    if (props.auth_method === 'api_key') {
      setShowManage(true);
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
  
  return (
    <>
      <Card className="w-full border shadow-none rounded-lg h-[204px]">
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
                <Badge variant="secondary" className="bg-green-50 text-green-700 dark:bg-green-900/30 dark:text-green-300 transition-colors">
                  Connected
                </Badge>
              )}
            </div>
            <div className="flex-1 min-w-0">
              <h2 className="text-lg font-semibold truncate">{props.name}</h2>
              <p className="text-muted-foreground mt-1 text-sm line-clamp-2">{props.description}</p>
            </div>
          </div>

          <div className="flex items-center mt-3 pt-3 justify-between gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleDocsClick}
            >
              Docs
              <Files className="h-4 w-4" />
            </Button>
            
            {!isPublic && (
              props.connected ? (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowManage(true)}
                >
                  {props.auth_method === 'api_key' ? 'Manage' : 'Manage'}
                  <ArrowUpRight className="h-4 w-4" />
                </Button>
              ) : (
                <Button 
                  variant="outline"
                  size="sm"
                  onClick={handleConnect}
                >
                  Connect
                  <Plus className="h-4 w-4" />
                </Button>
              )
            )}
          </div>
        </CardContent>
      </Card>

      {!isPublic && props.auth_method === 'api_key' && (
        <ManageDialog
          provider={props}
          open={showManage}
          onClose={() => setShowManage(false)}
          onUpdate={props.onConnectionChange || (() => {})}
        />
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