'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Header } from '@/app/modules/general/components/header';

export default function IntegrationAuthComplete() {
  const [status, setStatus] = useState('Completing authorization...');
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  const { provider_tag } = useParams<{ provider_tag: string }>();

  useEffect(() => {
    const processToken = async () => {
      try {
        const hash = window.location.hash.substring(1);
        let token;
        
        const match = hash.match(/token=([^&]+)/);
        if (match) {
          token = match[1];
        } else if (hash && hash.length > 20) {
          token = hash;
        }
        
        if (!token) {
          throw new Error('No token found in URL');
        }
        
        setStatus('Saving your authorization...');
        
        const response = await fetch(`/api/oauth/${provider_tag}/save-token`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ token })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
          throw new Error(data.error || 'Failed to save token');
        }
        
        setStatus('Authorization successful! Redirecting...');
        
        setTimeout(() => {
          router.push('/integrations?success=true');
        }, 1000);
      } catch (err: any) {
        setError(err.message || 'An unknown error occurred');
        console.error('Error processing token:', err);
      }
    };
    
    processToken();
  }, [router, provider_tag]);

  return (
    <div className="flex-1 flex flex-col relative h-[100vh] w-full">
      <Header isShowChat={false} />

      <div className="flex-1 px-8 py-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold tracking-tight">{provider_tag} Authorization</h1>
        </div>

        <div className="p-6 border rounded-lg flex flex-col items-center justify-center min-h-[40vh]">
          {error ? (
            <div className="text-red-500 font-medium text-center">
              <p className="mb-4">Error: {error}</p>
              <Button 
                onClick={() => router.push(`/integrations/${provider_tag}`)}
                className="mt-4"
              >
                Try Again
              </Button>
            </div>
          ) : (
            <div className="flex flex-col items-center">
              <Loader2 className="h-8 w-8 animate-spin mb-4" />
              <p className="text-lg">{status}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}