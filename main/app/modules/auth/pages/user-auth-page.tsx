'use client';

import { useEffect, useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { ManageDialog } from '@/app/modules/integrations/components/integration-manage';
import { ScopeDialog } from '@/app/modules/integrations/components/integration-settings';
import { getProviderDetails, initiateOAuthFlow } from '@/app/modules/integrations/api/api.integrations';

interface UserAuthPageProps {
  providerTag: string;
  code: string;
  apiKey?: string;
}

export function UserAuthPage({ providerTag, code, apiKey }: UserAuthPageProps) {
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState<string>('Authenticating...');
  const [initialized, setInitialized] = useState<boolean>(false);
  const [connectionComplete, setConnectionComplete] = useState<boolean>(false);
  const router = useRouter();
  
  const [showIntegrationDialog, setShowIntegrationDialog] = useState(false);
  const [showScopeDialog, setShowScopeDialog] = useState(false);
  const [encryptedApiKey, setEncryptedApiKey] = useState<string | null>(null);
  const [providerDetails, setProviderDetails] = useState<any>(null);
  const [verificationCode, setVerificationCode] = useState<string | null>(null);
  const verificationAttempted = useRef(false);

  useEffect(() => {
    setMessage('Authenticating...');
    setInitialized(true);
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
      if ((showIntegrationDialog || showScopeDialog) && providerTag) {
        try {
          const details = await getProviderDetails(providerTag);
          setProviderDetails(details.provider);
        } catch (error) {
          console.error("Error loading provider details:", error);
        }
      }
    };
    
    loadProviderDetails();
  }, [showIntegrationDialog, showScopeDialog, providerTag]);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      if (verificationAttempted.current) {
        return;
      }
    }

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
            api_key: apiKey 
          }),
        });

        if (!response.ok) {
          router.push(`/user/${providerTag}/auth?status_code=401&error=true`);
          throw new Error(`Authentication code is invalid or expired. Please generate a new url.`);
        }

        const data = await response.json();

        if (data.success) {
          if (data.encrypted_api_key) {
            setEncryptedApiKey(data.encrypted_api_key);
            setVerificationCode(data.code);
            setStatus('success');
            setMessage(`Establishing connection...`);
            
            try {
              const details = await getProviderDetails(providerTag);
              setProviderDetails(details.provider);
              
              if (details.provider.auth_method === 'oauth') {
                setTimeout(() => {
                  setShowScopeDialog(true);
                }, 1000);
              } else {
                setTimeout(() => {
                  setShowIntegrationDialog(true);
                }, 1000);
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
  }, [code, apiKey, providerTag, connectionComplete]);

  const handleUpdateIntegration = () => {
    
    setShowIntegrationDialog(false);
    setShowScopeDialog(false);
    
    setConnectionComplete(true);
    setStatus('success');
    setMessage('Provider successfully connected.');
    
    try {
      if (typeof window !== 'undefined') {
        const url = new URL(window.location.href);
        url.searchParams.set('success', 'true');
        window.history.replaceState({}, '', url.toString());
      }
    } catch (e) {
      console.error("Failed to update URL:", e);
    }
  };

  const handleCloseDialog = () => {
    setShowIntegrationDialog(false);
    setShowScopeDialog(false);
    
    if (!connectionComplete) {
      setStatus('error');
      setMessage('Integration setup was cancelled.');
    }
  };

  const handleScopeSelection = async (scopes: string[]) => {
    setShowScopeDialog(false);
    
    try {
      const baseReturnUrl = `/user/${providerTag}/auth`;
      const returnUrl = `${baseReturnUrl}?status_code=200&oauth_return=success`;
      
      const url = await initiateOAuthFlow(providerTag, scopes, returnUrl, encryptedApiKey || undefined, verificationCode || undefined);
      window.location.href = url;
    } catch (error) {
      console.error(`Failed to start OAuth flow for ${providerTag}:`, error);
      setStatus('error');
      setMessage('Failed to initiate authentication with selected permissions');
    }
  };

  const shouldShowMissingAuthMessage = () => {
    if (connectionComplete || showScopeDialog || showIntegrationDialog) {
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

  return (
    <div className="min-h-screen flex items-center justify-center bg-white">
      {connectionComplete ? (
        <div className="text-center">
          <p suppressHydrationWarning>Provider successfully connected.</p>
        </div>
      ) : showScopeDialog || showIntegrationDialog ? (
        <p className="text-black" suppressHydrationWarning>Loading provider settings...</p>
      ) : (
        <p className="text-black" suppressHydrationWarning>{getDisplayMessage()}</p>
      )}
      
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
    </div>
  );
}
