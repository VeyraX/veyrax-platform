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
  const router = useRouter();
  
  const [showIntegrationDialog, setShowIntegrationDialog] = useState(false);
  const [showScopeDialog, setShowScopeDialog] = useState(false);
  const [encryptedApiKey, setEncryptedApiKey] = useState<string | null>(null);
  const [providerDetails, setProviderDetails] = useState<any>(null);
  const [verificationCode, setVerificationCode] = useState<string | null>(null);
  const verificationAttempted = useRef(false);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const urlParams = new URLSearchParams(window.location.search);
      const success = urlParams.get('success');
      
      if (success === 'true') {
        setStatus('success');
        setMessage(`Provider successfully connected.`);
        return;
      }
    }
  }, []);

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
      const urlParams = new URLSearchParams(window.location.search);
      if (urlParams.get('success') === 'true' || verificationAttempted.current) {
        return;
      }
    }

    if (!code && !apiKey) {
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
  }, [code, apiKey, providerTag]);

  const handleCloseDialog = () => {
    setShowIntegrationDialog(false);
    setShowScopeDialog(false);
    router.push(`/user/${providerTag}/auth?success=true`);
  };

  const handleUpdateIntegration = () => {
    setShowIntegrationDialog(false);
    setShowScopeDialog(false);
    router.push(`/user/${providerTag}/auth?success=true`);
  };

  const handleScopeSelection = async (scopes: string[]) => {
    setShowScopeDialog(false);
    
    try {
      const returnUrl = `/user/${providerTag}/auth`;
      const url = await initiateOAuthFlow(providerTag, scopes, returnUrl, encryptedApiKey || undefined, verificationCode || undefined);
      window.location.href = url;
    } catch (error) {
      console.error(`Failed to start OAuth flow for ${providerTag}:`, error);
      setStatus('error');
      setMessage('Failed to initiate authentication with selected permissions');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-white">
      {showScopeDialog || showIntegrationDialog ? (
        <p className="text-black">Loading provider settings...</p>
      ) : (
        <p className="text-black">{message}</p>
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
