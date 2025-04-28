'use client';

import { useEffect, useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { ManageDialog } from '@/app/modules/integrations/components/integration-manage';
import { ScopeDialog } from '@/app/modules/integrations/components/integration-settings';
import { McpManage } from '@/app/modules/integrations/components/mcp/mcp-manage';
import { initiateOAuthFlow, getProviderAuthInfo } from '@/app/modules/integrations/api/api.integrations';
import { getMcpDetailsByImageName } from '@/app/modules/integrations/api/api.integrations.mcp';
import { Copy, Check, ExternalLink } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface UserAuthPageProps {
  providerTag: string;
  code: string;
  apiKey?: string;
  type?: string;
  returnUrl?: string;
}

export function UserAuthPage({ providerTag, code, apiKey, type, returnUrl }: UserAuthPageProps) {
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState<string>('Authenticating...');
  const [initialized, setInitialized] = useState<boolean>(false);
  const [connectionComplete, setConnectionComplete] = useState<boolean>(false);
  const router = useRouter();
  
  const [isRedirecting, setIsRedirecting] = useState<boolean>(false);
  const [showIntegrationDialog, setShowIntegrationDialog] = useState(false);
  const [showScopeDialog, setShowScopeDialog] = useState(false);
  const [showMcpDialog, setShowMcpDialog] = useState(false);
  const [encryptedApiKey, setEncryptedApiKey] = useState<string | null>(null);
  const [providerDetails, setProviderDetails] = useState<any>(null);
  const [mcpDetails, setMcpDetails] = useState<any>(null);
  const [verificationCode, setVerificationCode] = useState<string | null>(null);
  const verificationAttempted = useRef(false);
  const isMcp = type === 'mcp';
  const [copied, setCopied] = useState(false);
  const [isMobile, setIsMobile] = useState(false);

  const extractUid = () => {
    if (!returnUrl) return null;
    
    try {
      let match = returnUrl.match(/prompt=uid=([^&]+)/);
      
      if (match) {
        return match[1];
      }
      
      const decodedUrl = decodeURIComponent(returnUrl);
      match = decodedUrl.match(/Paste\s+this\s+UID\s+in\s+ChatGPT\s+([a-zA-Z0-9]+)/);
      
      return match ? match[1] : null;
    } catch (error) {
      console.error("Error extracting UID:", error);
      return null;
    }
  };

  const uid = extractUid();

  const copyToClipboard = () => {
    if (uid) {
      navigator.clipboard.writeText(`Omi UID: ${uid}`).then(() => {
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      });
    }
  };

  useEffect(() => {
    setMessage('Authenticating...');
    setInitialized(true);
    
    const checkMobile = () => {
      const userAgent = navigator.userAgent || navigator.vendor || (window as any).opera;
      const isMobileByAgent = /android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(userAgent.toLowerCase());
      const isMobileBySize = typeof window !== 'undefined' && window.innerWidth <= 768;
      setIsMobile(isMobileByAgent || isMobileBySize);
    };
    
    if (typeof window !== 'undefined') {
      checkMobile();
      window.addEventListener('resize', checkMobile);
      return () => window.removeEventListener('resize', checkMobile);
    }
  }, []);

  useEffect(() => {
    if (!initialized) return;
    
    if (typeof window !== 'undefined') {
      const url = window.location.href;
      
      if (url.includes('oauth_return=success') && url.includes('status_code=200')) {
        setConnectionComplete(true);
        setStatus('success');
        setMessage('Provider successfully connected.');
        return;
      }
      
      if (url.includes('success=true')) {
        setConnectionComplete(true);
        setStatus('success');
        setMessage('Provider successfully connected.');
        return;
      }
    }
  }, [initialized]);

  useEffect(() => {
    const loadProviderDetails = async () => {
      if (showMcpDialog && providerTag && isMcp) {
        try {
          const details = await getMcpDetailsByImageName(providerTag);
          if (details) {
            setMcpDetails(details);
          }
        } catch (error) {
          console.error("Error loading MCP details:", error);
        }
      } else if ((showIntegrationDialog || showScopeDialog) && providerTag && !isMcp) {
        try {
          const details = await getProviderAuthInfo(providerTag);
          if (details) {
            setProviderDetails({
              ...details,
              connected: false
            });
          }
        } catch (error) {
          console.error("Error loading provider details:", error);
        }
      }
    };
    
    loadProviderDetails();
  }, [showIntegrationDialog, showScopeDialog, showMcpDialog, providerTag, isMcp]);

  useEffect(() => {
    if (connectionComplete) {
      return;
    }

    if (!code && !apiKey) {
      if (typeof window !== 'undefined') {
        const url = window.location.href;
        if (url.includes('oauth_return=success') || url.includes('success=true')) {
          return;
        }
      }
      return;
    }
    
    const verifyAuth = async () => {
      verificationAttempted.current = true;
      
      try {
        const response = await fetch('/api/auth/verify', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ 
            code,
            api_key: apiKey,
            type
          }),
        });

        if (!response.ok) {
          router.push(`/user/${providerTag}/auth?status_code=401&error=true`);
          throw new Error(`Authentication code is invalid or expired. Please generate a new url.`);
        }

        const data = await response.json();

        if (data.success) {
          if (data.redirect_url) {
            setMessage('Connection already exists. Redirecting...');
            setIsRedirecting(true);
            
            if (isMobile) {
              setStatus('success');
            } else {
              router.push(data.redirect_url);
            }
            return;
          }

          if (data.encrypted_api_key) {
            setEncryptedApiKey(data.encrypted_api_key);
            setVerificationCode(data.code);
            setStatus('success');
            setMessage(`Establishing connection...`);
            
            try {
              if (isMcp) {
                // Handle MCP connection
                const details = await getMcpDetailsByImageName(providerTag);
                if (details) {
                  setMcpDetails(details);
                  setTimeout(() => {
                    setShowMcpDialog(true);
                  }, 1000);
                } else {
                  throw new Error(`MCP image ${providerTag} not found`);
                }
              } else {
                // Handle regular provider connection
                const authInfo = await getProviderAuthInfo(providerTag);
                
                if (authInfo) {
                  setProviderDetails({
                    ...authInfo,
                    connected: false
                  });
                  
                  if (authInfo.auth_method === 'oauth') {
                    setTimeout(() => {
                      setShowScopeDialog(true);
                    }, 1000);
                  } else {
                    setTimeout(() => {
                      setShowIntegrationDialog(true);
                    }, 1000);
                  }
                } else {
                  throw new Error('Could not determine provider authentication method');
                }
              }
            } catch (error) {
              console.error("Error loading provider details:", error);
              setStatus('error');
              setMessage('Error loading provider details');
            }
          } else {
            throw new Error('Authentication successful, but no API key received.');
          }
        } else {
          throw new Error(data.error || 'Authentication failed');
        }
      } catch (error) {
        console.error('Authentication error:', error);
        setStatus('error');
        setMessage(error instanceof Error ? error.message : 'An error occurred during authentication');
      }
    };

    verifyAuth();
  }, [code, apiKey, providerTag, connectionComplete, isMcp, type, isMobile, router]);

  useEffect(() => {
    if (connectionComplete && returnUrl) {
      setIsRedirecting(true);
      if (isMobile) {
        setMessage('Provider successfully connected.');
      } else {
        setMessage('Redirecting...');
        setTimeout(() => {
          window.location.href = returnUrl;
        }, 1500);
      }
    }
  }, [connectionComplete, returnUrl, isMobile]);

  const handleManualRedirect = () => {
    if (returnUrl) {
      window.location.href = returnUrl;
    }
  };

  const handleUpdateIntegration = async () => {
    setShowIntegrationDialog(false);
    setShowScopeDialog(false);
    setShowMcpDialog(false);
    
    setConnectionComplete(true);
    setStatus('success');
    
    if (isMobile) {
      setMessage('Provider successfully connected.');
    } else {
      setMessage('Provider successfully connected. Redirecting...');
      setTimeout(() => {
        if (returnUrl) {
          window.location.href = returnUrl;
        }
      }, 1500);
    }
  };

  const handleCloseDialog = () => {
    setShowIntegrationDialog(false);
    setShowScopeDialog(false);
    setShowMcpDialog(false);
    
    if (!connectionComplete) {
      setStatus('error');
      setMessage('Integration setup was cancelled.');
    }
  };

  const handleScopeSelection = async (scopes: string[]) => {
    setShowScopeDialog(false);
    
    try {
      const baseReturnUrl = `/user/${providerTag}/auth?returnUrl=${returnUrl}`;
      const finalReturnUrl = `${baseReturnUrl}&status_code=200&oauth_return=success`;
      
      const url = await initiateOAuthFlow(providerTag, scopes, finalReturnUrl, encryptedApiKey || undefined, verificationCode || undefined);
      window.location.href = url;
    } catch (error) {
      console.error(`Failed to start OAuth flow for ${providerTag}:`, error);
      setStatus('error');
      setMessage('Failed to initiate authentication with selected permissions');
    }
  };

  const shouldShowMissingAuthMessage = () => {
    if (connectionComplete || showScopeDialog || showIntegrationDialog || showMcpDialog) {
      return false;
    }
    
    if (!code && !apiKey) {
      if (typeof window !== 'undefined') {
        const url = window.location.href;
        return !(url.includes('oauth_return=success') || url.includes('success=true'));
      }
      return true;
    }
    
    return false;
  };

  const getDisplayMessage = () => {
    if (!initialized) {
      return '';
    }

    if (shouldShowMissingAuthMessage()) {
      return 'Authentication code missing. Please use a valid authentication link.';
    }
    
    return message;
  };

  const renderUidDisplay = () => {
    if (!uid || !connectionComplete || !isMobile) return null;
    
    return (
      <div className="mb-4">
        <div className="text-center mb-2">
          <h2 className="font-medium text-lg">Step 1: Copy Your Omni ID</h2>
        </div>
        <div className="flex items-center justify-center space-x-1 cursor-pointer group" onClick={copyToClipboard}>
          <span className="font-mono text-gray-700 group-hover:text-gray-900">{uid}</span>
          {copied ? <Check size={16} className="text-green-500" /> : <Copy size={16} className="text-gray-400 group-hover:text-gray-600" />}
        </div>
      </div>
    );
  };

  const renderRedirectButton = () => {
    if (!returnUrl || !connectionComplete || !isMobile) return null;
    
    return (
      <div className="mt-4 flex flex-col items-center">
        <div className="text-center mb-2">
          <h2 className="font-medium text-lg">Step 2: Go to ChatGPT and paste your Omni ID</h2>
        </div>
        <Button 
          onClick={handleManualRedirect}
          className="flex items-center justify-center gap-2 mx-auto"
        >
          Continue in ChatGPT
        </Button>
      </div>
    );
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-white">
      <div className="text-center">
        <p className="text-foreground mb-4" suppressHydrationWarning>{getDisplayMessage()}</p>
        {renderUidDisplay()}
        {renderRedirectButton()}
      </div>
      
      {showScopeDialog && providerDetails && (
        <ScopeDialog
          provider={providerDetails}
          open={showScopeDialog}
          onClose={handleCloseDialog}
          onConfirm={handleScopeSelection}
        />
      )}

      {showIntegrationDialog && providerDetails && (
        <ManageDialog 
          provider={providerDetails}
          open={showIntegrationDialog}
          onClose={handleCloseDialog}
          onUpdate={handleUpdateIntegration}
          encrypted_api_key={encryptedApiKey || undefined}
          code={verificationCode || undefined}
        />
      )}
      
      {showMcpDialog && mcpDetails && (
        <McpManage
          imageName={mcpDetails.image_name || providerTag}
          open={showMcpDialog}
          onClose={handleCloseDialog}
          predefinedEnv={mcpDetails.env || {}}
          repositoryId={mcpDetails.id}
          onConnectionUpdate={handleUpdateIntegration}
          encrypted_api_key={encryptedApiKey || undefined}
          code={verificationCode || undefined}
        />
      )}
    </div>
  );
}
