'use client'

import { FC, useState } from 'react'
import { Card, CardContent, CardHeader, CardFooter } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ArrowUpRight, Plus } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { IntegrationCardProps } from '../api/types.integrations'
import { useRouter } from 'next/navigation'
import { ScopeDialog } from './integration-settings'
import { Provider } from '../api/types.integrations'
import { disconnectProvider, deleteProviderIndex, initiateOAuthFlow, enableApiKeyProvider, createProviderIndex } from '../api/api.integrantions'


export const IntegrationCard: FC<IntegrationCardProps> = (props) => {
  const router = useRouter()
  const [showSettings, setShowSettings] = useState(false);

  const handleShowSettings = (provider: Provider) => {
    setShowSettings(true);
  };

  const handleSettingsClose = () => {
    setShowSettings(false);
  };

  const handleSettingsConfirm = async (scopes: string[], enableIndex: boolean) => {
    setShowSettings(false);
    try {
      const url = await initiateOAuthFlow(props.provider_tag, scopes);
      window.location.href = url;
    } catch (error) {
      console.error(`Failed to start OAuth flow for ${props.name}:`, error);
    }
  };

  const handleApiKeyEnable = async () => {
    try {
      await enableApiKeyProvider(props.id);
      props.onConnectionChange?.();
    } catch (error) {
      console.error(`Failed to enable ${props.name}:`, error);
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
              {props.connected && (
                <Badge variant="secondary" className="bg-green-100 text-green-800">
                  Connected
                </Badge>
              )}
            </div>
            <div className="flex-1 min-w-0">
              <h2 className="text-lg font-semibold truncate">{props.name}</h2>
              <p className="text-muted-foreground mt-1 text-sm line-clamp-2">{props.description}</p>
            </div>
          </div>

          <div className="flex items-center mt-3 pt-3 justify-between">
            {props.connected && props.has_index_capability && (
              <Button 
                variant="ghost" 
                className={props.hasIndex ? "text-red-600 hover:text-red-700 hover:bg-red-50" : ""}
                onClick={async () => {
                  try {
                    if (props.hasIndex) {
                      await deleteProviderIndex(props.id);
                    } else {
                      await createProviderIndex(props.id, props.provider_tag);
                    }
                    props.onConnectionChange?.();
                  } catch (error) {
                    console.error(`Failed to ${props.hasIndex ? 'delete' : 'create'} index for ${props.name}:`, error);
                  }
                }}
              >
                {props.hasIndex ? 'Delete Index' : 'Index Data'}
              </Button>
            )}
            
            {props.connected ? (
              <Button 
                variant="ghost" 
                className="text-red-600 hover:text-red-700 hover:bg-red-50"
                onClick={async () => {
                  try {
                    await disconnectProvider(props.id);
                    props.onConnectionChange?.();
                  } catch (error) {
                    console.error(`Failed to disconnect ${props.name}:`, error);
                  }
                }}
              >
                Disconnect
              </Button>
            ) : (
              <Button 
                variant="outline"
                onClick={() => {
                  if (props.auth_method === 'api_key') {
                    handleApiKeyEnable();
                  } else {
                    handleShowSettings(props as Provider);
                  }
                }}
              >
                {props.auth_method === 'api_key' ? 'Enable' : 'Connect'}
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      {props.auth_method === 'oauth' && (
        <ScopeDialog
          provider={{
            id: props.id,
            name: props.name,
            description: props.description,
            logo_url: props.logo_url,
            provider_tag: props.provider_tag,
            auth_method: props.auth_method as 'oauth' | 'api_key',
            scopes: props.scopes,
            has_index_capability: props.has_index_capability
          }}
          open={showSettings}
          onClose={handleSettingsClose}
          onConfirm={handleSettingsConfirm}
        />
      )}
    </>
  )
}