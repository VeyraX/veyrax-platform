'use client';

import { Suspense, useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';

function OmiRedirectContent() {
  'use client';

  const searchParams = useSearchParams();
  const [status, setStatus] = useState<'loading' | 'error' | 'redirecting'>('loading');
  const [message, setMessage] = useState<string>('Initializing...');

  useEffect(() => {
    setMessage('Reading parameters...');
    const omiUserId = searchParams.get('omi_user_id');
    const providerTag = searchParams.get('provider_tag');

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

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.error || 'Failed to generate connection link');
        }

        if (data.success && data.link) {
          setStatus('redirecting');
          setMessage('Redirecting to provider...');
          window.location.href = data.link;
        } else {
          throw new Error('Invalid response received from the server.');
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

  }, [searchParams]);


  return (
    <>
      <p className="text-foreground" suppressHydrationWarning>{message}</p>
      {status === 'loading' && (
        <div className="mt-4">
          <svg className="animate-spin h-5 w-5 text-primary" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </div>
      )}
      {status === 'error' && (
         <p className="mt-4 text-destructive font-semibold" suppressHydrationWarning>Please check the console for details or try again.</p>
      )}
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
