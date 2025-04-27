'use client';

import { Suspense, useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';

function AuthCallbackContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function handleAuthCallback() {
      try {
        // Check if we have a code in query params
        const code = searchParams.get('code');
        const next = searchParams.get('next') || '/agent';

        console.log("[handle auth callback]", searchParams)
        
        // If we have hash tokens, redirect to API with the tokens in query params
        if (window.location.hash) {
          const hashParams = new URLSearchParams(window.location.hash.substring(1));
          const accessToken = hashParams.get('access_token');
          const refreshToken = hashParams.get('refresh_token');
          const expiresIn = hashParams.get('expires_in');
          const expiresAt = hashParams.get('expires_at');
          
          if (accessToken && refreshToken) {
            // Build API URL with all parameters
            const apiUrl = new URL('/api/auth/callback', window.location.origin);
            apiUrl.searchParams.set('access_token', accessToken);
            apiUrl.searchParams.set('refresh_token', refreshToken);
            if (expiresIn) apiUrl.searchParams.set('expires_in', expiresIn);
            if (expiresAt) apiUrl.searchParams.set('expires_at', expiresAt);
            apiUrl.searchParams.set('next', next);
            
            // Redirect to API endpoint
            window.location.href = apiUrl.toString();
            return;
          }
        }
        
        // If we have code or tokens in query params, redirect to API
        if (code || searchParams.get('access_token')) {
          // Build API URL with all parameters
          const apiUrl = new URL('/api/auth/callback', window.location.origin);
          searchParams.forEach((value, key) => {
            apiUrl.searchParams.set(key, value);
          });
          
          // Redirect to API endpoint
          window.location.href = apiUrl.toString();
          return;
        }

        setError('Missing authentication parameters');
        router.push('/login?error=missing_token');
      } catch (err: any) {
        console.error('Auth callback error:', err);
        setError(err.message || 'Authentication failed');
        router.push(`/login?error=${encodeURIComponent(err.message || 'unknown')}`);
      }
    }

    handleAuthCallback();
  }, [searchParams, router]);

  return (
    <div className="flex items-center justify-center min-h-screen">
      {error ? (
        <div className="text-red-500">
          <p>Authentication error: {error}</p>
        </div>
      ) : (
        <div className="text-center">
          <p className="mb-4">Authenticating...</p>
          <div className="w-8 h-8 border-t-2 border-b-2 border-gray-900 rounded-full animate-spin mx-auto"></div>
        </div>
      )}
    </div>
  );
}

export default function AuthCallbackPage() {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <p className="mb-4">Loading...</p>
          <div className="w-8 h-8 border-t-2 border-b-2 border-gray-900 rounded-full animate-spin mx-auto"></div>
        </div>
      </div>
    }>
      <AuthCallbackContent />
    </Suspense>
  );
} 