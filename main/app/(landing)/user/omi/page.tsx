'use client';

import { Suspense, useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { Copy, Check, ExternalLink } from 'lucide-react';
import { Button } from '@/components/ui/button';

function OmiRedirectContent() {
  'use client';

  const searchParams = useSearchParams();
  const [status, setStatus] = useState<'loading' | 'error' | 'redirecting'>('loading');
  const [message, setMessage] = useState<string>('Initializing...');
  const [isMobile, setIsMobile] = useState(false);
  const [copied, setCopied] = useState(false);
  const [connectionUrl, setConnectionUrl] = useState<string | null>(null);

  const omiUserId = searchParams.get('omi_user_id');
  const providerTag = searchParams.get('provider_tag');

  const copyToClipboard = () => {
    if (omiUserId) {
      navigator.clipboard.writeText(`Omi UID: ${omiUserId}`).then(() => {
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      });
    }
  };

  useEffect(() => {
    const checkMobile = () => {
      const userAgent = navigator.userAgent || navigator.vendor || (window as any).opera;
      const ua = userAgent.toLowerCase();
      
      const isMobileByAgent = /android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(ua);
      const isMobileBySize = typeof window !== 'undefined' && window.innerWidth <= 768;
      
      const isIos = /iphone|ipod|ipad/.test(ua);
      const isAndroid = /android/.test(ua);
      const safari = /safari/.test(ua);
      
      const isIosWebview = isIos && !safari;
      
      const isAndroidWebview = isAndroid && (/wv/.test(ua) || 
        (/Version\//.test(ua) && !/Chrome\//.test(ua)));
      
      setIsMobile(isMobileByAgent || isMobileBySize || isIosWebview || isAndroidWebview);
    };
    
    if (typeof window !== 'undefined') {
      checkMobile();
      window.addEventListener('resize', checkMobile);
      return () => window.removeEventListener('resize', checkMobile);
    }
  }, []);

  useEffect(() => {
    setMessage('Reading parameters...');
    
    if (!omiUserId || !providerTag) {
      setMessage('Error: Missing required parameters (omi_user_id and provider_tag) in the URL.');
      setStatus('error');
      return;
    }

    const callApi = async () => {
      setStatus('loading');
      setMessage(`Fetching connection link for ${providerTag}...`);
      try {
        const response = await fetch('/api/integrations/generate-connection-link', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            omi_user_id: omiUserId,
            provider_tag: providerTag,
          }),
        });

        const responseData = await response.json();

        if (response.ok) {
          if (responseData.data && responseData.data.redirect_url) {
            setStatus('redirecting');
            setMessage(responseData.data.message || 'Provider already connected.');
            setConnectionUrl(responseData.data.redirect_url);
            
            if (!isMobile && responseData.data.redirect_url) {
              window.location.href = responseData.data.redirect_url;
            }
            
          } else if (responseData.data && responseData.data.connection_url) {
            setStatus('redirecting');
            setMessage('Redirecting to provider...');
            window.location.href = responseData.data.connection_url;
          } else {
            throw new Error(responseData.data?.error || responseData.data?.detail || 'Invalid successful response from API. Missing connection_url or redirect_url.');
          }
        } else {
          if (responseData.data && responseData.data.redirect_url) {
            setStatus('redirecting');
            setMessage(responseData.data.message || 'Redirecting based on API instruction...');
            setConnectionUrl(responseData.data.redirect_url);
            
            if (!isMobile && responseData.data.redirect_url) {
              window.location.href = responseData.data.redirect_url;
            }
            
          } else {
            throw new Error(responseData.data?.error || responseData.data?.detail || `Request failed with status ${response.status}`);
          }
        }
      } catch (err: any) {
        console.error('API call failed:', err);
        setMessage(err.message || 'An unexpected error occurred while fetching the link.');
        setStatus('error');
      }
    };

    const timer = setTimeout(() => {
      callApi();
    }, 100);

    return () => clearTimeout(timer);

  }, [omiUserId, providerTag, isMobile]);

  const handleManualRedirect = () => {
    if (connectionUrl) {
      window.location.href = connectionUrl;
    }
  };

  const renderUidDisplay = () => {
    if (!omiUserId || status !== 'redirecting' || !connectionUrl || !isMobile) return null;
    
    return (
      <div className="mb-4">
        <div className="text-center mb-2">
          <h2 className="font-medium text-lg">Step 1: Copy Your Omni ID</h2>
        </div>
        <div className="flex items-center justify-center space-x-1 cursor-pointer group" onClick={copyToClipboard}>
          <span className="font-mono text-gray-700 group-hover:text-gray-900">{omiUserId}</span>
          {copied ? <Check size={16} className="text-green-500" /> : <Copy size={16} className="text-gray-400 group-hover:text-gray-600" />}
        </div>
      </div>
    );
  };

  const renderChatGptButton = () => {
    if (!connectionUrl || status !== 'redirecting' || !isMobile) return null;
    
    return (
      <div className="mt-4 flex flex-col items-center">
        <div className="text-center mb-2">
          <h2 className="font-medium text-lg">Step 2: Go to ChatGPT and paste your Omni ID</h2>
        </div>
        <Button 
          onClick={handleManualRedirect}
          className="flex items-center justify-center gap-2 mx-auto"
        >
          Open in ChatGPT
        </Button>
      </div>
    );
  };

  return (
    <>
      <p className="text-foreground mb-4" suppressHydrationWarning>{message}</p>
      {status === 'loading' && (
        <div className="mt-4 mb-4">
          <svg className="animate-spin h-5 w-5 text-primary mx-auto" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </div>
      )}
      {renderUidDisplay()}
      {renderChatGptButton()}
    </>
  );
}


export default function OmiRedirectPage() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-5 text-center bg-background">
      <Suspense fallback={<p className="text-foreground">Loading page...</p>}>
        <OmiRedirectContent />
      </Suspense>
    </div>
  );
}
