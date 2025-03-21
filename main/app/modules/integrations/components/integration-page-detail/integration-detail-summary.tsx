import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { 
  PlusIcon, 
  GlobeIcon, 
  ArrowUpRightIcon, 
  TargetIcon, 
  SettingsIcon,
  ChevronUpIcon
} from "lucide-react"
import { IntegrationDetailSummaryProps } from "../../api/types.integrations"
import { useEffect, useState } from "react"
import { ScopeDialog } from '../integration-settings'
import { ManageDialog } from '../integration-manage'
import { initiateOAuthFlow } from '../../api/api.integrations'
import { getIntegrationsData } from '../../api/api.integrations'
import { enableProvider } from '../../api/api.integrations'

interface IntegrationDetailSummaryPropsWithPublic extends IntegrationDetailSummaryProps {
  isPublic?: boolean
}

export default function IntegrationDetailSummary({ providerDetails, isPublic = false }: IntegrationDetailSummaryPropsWithPublic) {
  const { provider, totalEndpoints, totalParameters, totalComponents, endpointsList } = providerDetails
  const [showScrollTop, setShowScrollTop] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [showManage, setShowManage] = useState(false);
  const [isConnected, setIsConnected] = useState(false);

  // Parse categories string into an array
  const categories = provider.categories 
    ? provider.categories.split(',').map(category => category.trim())
    : [];

  useEffect(() => {
    const handleAnchorClick = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      const anchorLink = target.closest('a[href^="#"]');
      
      if (anchorLink) {
        e.preventDefault();
        const targetId = anchorLink.getAttribute('href')?.substring(1);
        
        if (targetId) {
          const targetElement = document.getElementById(targetId);
          
          if (targetElement) {
            window.scrollTo({
              top: targetElement.offsetTop - 80, 
              behavior: 'smooth'
            });
            
            targetElement.classList.add('highlight-target');
            setTimeout(() => {
              targetElement.classList.remove('highlight-target');
            }, 2000);
          }
        }
      }
    };

    const handleScroll = () => {
      setShowScrollTop(window.scrollY > 300);
    };

    document.addEventListener('click', handleAnchorClick);
    window.addEventListener('scroll', handleScroll);
    
    return () => {
      document.removeEventListener('click', handleAnchorClick);
      window.removeEventListener('scroll', handleScroll);
    };
  }, []);

  useEffect(() => {
    if (!isPublic) {
      const checkConnection = async () => {
        try {
          const providers = await getIntegrationsData();
          const currentProvider = providers.find(p => p.provider_tag === provider.provider_tag);
          setIsConnected(currentProvider?.connected || false);
        } catch (error) {
          console.error('Failed to check connection status:', error);
          setIsConnected(false);
        }
      };
      
      checkConnection();
    }
  }, [provider.provider_tag, isPublic]);

  const scrollToTop = () => {
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  };

  const handleConnect = () => {
    if (isConnected) {
      setShowManage(true);
    } else {
      if (provider.provider_tag && provider.provider_tag.toLowerCase() === 'veyrax') {
        const enableVeyraxProvider = async () => {
          try {
            await enableProvider(provider.id);
            const providers = await getIntegrationsData();
            const currentProvider = providers.find(p => p.provider_tag === provider.provider_tag);
            setIsConnected(currentProvider?.connected || false);
          } catch (error) {
            console.error(`Failed to connect ${provider.name}:`, error);
          }
        };
        
        enableVeyraxProvider();
        return;
      }
      
      if (provider.auth_method === 'api_key' || 
          provider.auth_method === 'api_key_with_base' || 
          provider.auth_method === 'db_access' ||
          provider.auth_method === 'custom') {
        setShowManage(true);
      } else if (provider.auth_method === 'none') {
        const enableNoneProvider = async () => {
          try {
            await enableProvider(provider.id);
            const providers = await getIntegrationsData();
            const currentProvider = providers.find(p => p.provider_tag === provider.provider_tag);
            setIsConnected(currentProvider?.connected || false);
          } catch (error) {
            console.error(`Failed to connect ${provider.name}:`, error);
          }
        };
        
        enableNoneProvider();
      } else {
        setShowSettings(true);
      }
    }
  };

  const handleSettingsClose = () => {
    setShowSettings(false);
  };

  const handleSettingsConfirm = async (scopes: string[]) => {
    setShowSettings(false);
    try {
      const url = await initiateOAuthFlow(provider.provider_tag, scopes);
      window.location.href = url;
    } catch (error) {
      console.error(`Failed to start OAuth flow for ${provider.name}:`, error);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-background relative">
      <main className="flex-1">
        <div className="flex flex-col md:flex-row justify-between items-start mb-6">
          <div className="flex items-start gap-4">
            {provider.logo_url && (
              <div className="w-12 h-12 flex-shrink-0 rounded-lg overflow-hidden">
                <img 
                  src={provider.logo_url} 
                  alt={`${provider.name} logo`} 
                  className="w-full h-full object-contain"
                />
              </div>
            )}
            <div>
              <div className="flex items-center gap-2 mb-2">
                <h1 className="text-3xl font-bold text-foreground">{provider.name}</h1>
              </div>
              <p className="text-muted-foreground mt-4">{provider.description}</p>
            </div>
          </div>
          {!isPublic && (
            <Button 
              className="mt-4 md:mt-0" 
              onClick={handleConnect}
              size="sm"
              variant={isConnected ? "outline" : "default"}
            >
              {isConnected ? (
                <>
                  Manage
                  <ArrowUpRightIcon className="h-4 w-4" />
                </>
              ) : (
                <>
                  Connect
                  <PlusIcon className="h-4 w-4" />
                </>
              )}
            </Button>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <div className="border border-border rounded-lg p-6 bg-card">
            <div className="flex items-start gap-3">
              <div className="p-2 bg-muted rounded-md">
                <ArrowUpRightIcon size={18} className="text-foreground" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-foreground">{totalEndpoints}</h2>
                <p className="text-muted-foreground">Total Actions</p>
              </div>
            </div>
          </div>
          <div className="border border-border rounded-lg p-6 bg-card">
            <div className="flex items-start gap-3">
              <div className="p-2 bg-muted rounded-md">
                <TargetIcon size={18} className="text-foreground" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-foreground">{totalParameters}</h2>
                <p className="text-muted-foreground">Total Parameters</p>
              </div>
            </div>
          </div>
          <div className="border border-border rounded-lg p-6 bg-card">
            <div className="flex items-start gap-3">
              <div className="p-2 bg-muted rounded-md">
                <SettingsIcon size={18} className="text-foreground" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-foreground">{totalComponents}</h2>
                <p className="text-muted-foreground">UI Components</p>
              </div>
            </div>
          </div>
        </div>

        <div className="border border-border rounded-lg p-6 mb-8 bg-card">
          <h2 className="text-lg font-bold mb-1 text-foreground">Available Actions</h2>
          <p className="text-muted-foreground mb-6">
            Contains {totalEndpoints} actions that agents can invoke with natural language.
          </p>

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="text-left text-muted-foreground">
                  <th className="pb-4 font-medium w-1/4">Action</th>
                  <th className="pb-4 font-medium w-2/5">Description</th>
                  <th className="pb-4 font-medium text-center w-1/6">Parameters</th>
                  <th className="pb-4 font-medium text-right w-1/6"></th>
                </tr>
              </thead>
              <tbody>
                {endpointsList.map((endpoint, index) => (
                  <tr key={index} className="border-t border-border">
                    <td className="py-4 pr-4">
                      <div className="font-medium text-foreground">{endpoint.name}</div>
                      <div className="text-sm text-muted-foreground">{endpoint.functionId}</div>
                    </td>
                    <td className="py-4 pr-4 text-muted-foreground">
                      {endpoint.description}
                    </td>
                    <td className="py-4 text-center text-muted-foreground">{endpoint.paramCount}</td>
                    <td className="py-4 text-right">
                      <Button 
                        variant="link" 
                        size="icon"
                        onClick={(e) => {
                          e.preventDefault();
                          const targetElement = document.getElementById(endpoint.name);
                          if (targetElement) {
                            window.scrollTo({
                              top: targetElement.offsetTop - 80,
                              behavior: 'smooth'
                            });
                            targetElement.classList.add('highlight-target');
                            setTimeout(() => {
                              targetElement.classList.remove('highlight-target');
                            }, 2000);
                          }
                        }}
                      >
                        <ArrowUpRightIcon size={14} />
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Database documentation block */}
        {['snowflake', 'clickhouse', 'postgres', 'postgresql'].includes(provider.provider_tag.toLowerCase()) && (
          <div className="border border-border rounded-lg p-6 mb-8 bg-card flex justify-between items-center">
            <span className="text-foreground font-medium">How-To Documentation</span>
            <Button 
              variant="link"
              size="sm"
              onClick={() => window.open(`https://docs.veyrax.com/integrations/${provider.provider_tag.toLowerCase()}`, '_blank')}
              className="flex items-center gap-2 text-primary"
            >
              <ArrowUpRightIcon className="h-4 w-4" />
            </Button>
          </div>
        )}

        {/* HTTP Request documentation block */}
        {provider.provider_tag.toLowerCase() === 'http-request' && (
          <div className="border border-border rounded-lg p-6 mb-8 bg-card flex justify-between items-center">
            <span className="text-foreground font-medium">How to Use for Local Development</span>
            <Button 
              variant="link"
              size="sm"
              onClick={() => window.open('https://docs.veyrax.com/http-request-tool', '_blank')}
              className="flex items-center gap-2 text-primary"
            >
              <ArrowUpRightIcon className="h-4 w-4" />
            </Button>
          </div>
        )}
      </main>

      {showScrollTop && (
        <Button
          variant="default"
          size="icon"
          className="fixed bottom-4 right-4 rounded-full shadow-md h-8 w-8 p-0 flex items-center justify-center"
          onClick={scrollToTop}
          aria-label="Scroll to top"
        >
          <ChevronUpIcon size={16} />
        </Button>
      )}

      {!isPublic && (
        (provider.auth_method === 'api_key' || 
         provider.auth_method === 'api_key_with_base' || 
         provider.auth_method === 'db_access' || 
         provider.auth_method === 'custom' || 
         (provider.provider_tag && provider.provider_tag.toLowerCase() === 'veyrax') ||
         (provider.auth_method === 'none' && isConnected)) && (
          <ManageDialog
            provider={{
              ...provider,
              connected: isConnected,
              hasIndex: false,
              indexStatus: null
            }}
            open={showManage}
            onClose={() => setShowManage(false)}
            onUpdate={() => {
              const checkConnection = async () => {
                try {
                  const providers = await getIntegrationsData();
                  const currentProvider = providers.find(p => p.provider_tag === provider.provider_tag);
                  setIsConnected(currentProvider?.connected || false);
                } catch (error) {
                  console.error('Failed to check connection status:', error);
                }
              };
              
              checkConnection();
            }}
          />
        )
      )}
      
      {!isPublic && provider.auth_method === 'oauth' && isConnected && (
        <ManageDialog
          provider={{
            ...provider,
            connected: isConnected,
            hasIndex: false,
            indexStatus: null
          }}
          open={showManage}
          onClose={() => setShowManage(false)}
          onUpdate={() => {
            const checkConnection = async () => {
              try {
                const providers = await getIntegrationsData();
                const currentProvider = providers.find(p => p.provider_tag === provider.provider_tag);
                setIsConnected(currentProvider?.connected || false);
              } catch (error) {
                console.error('Failed to check connection status:', error);
              }
            };
            
            checkConnection();
          }}
        />
      )}

      {!isPublic && provider.auth_method === 'oauth' && (
        <ScopeDialog
          provider={{
            id: provider.id,
            name: provider.name,
            description: provider.description,
            logo_url: provider.logo_url,
            provider_tag: provider.provider_tag,
            auth_method: provider.auth_method as 'oauth' | 'api_key',
            scopes: provider.scopes,
          }}
          open={showSettings}
          onClose={handleSettingsClose}
          onConfirm={handleSettingsConfirm}
        />
      )}
    </div>
  )
}

