'use client';

import { useEffect, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import Link from 'next/link';

type SessionStatus = 'loading' | 'success' | 'not_found' | 'error';

export default function PaymentSuccess() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [status, setStatus] = useState<SessionStatus>('loading');
  const [errorMessage, setErrorMessage] = useState<string>('');
  const sessionId = searchParams.get('session_id');

  useEffect(() => {
    if (!sessionId) {
      router.push('/pricing');
      return;
    }
    
    const verifySession = async () => {
      try {
        const response = await fetch(`/api/stripe/checkout_sessions/${sessionId}`);
        
        if (response.status === 404) {
          setStatus('not_found');
          return;
        }
        
        if (!response.ok) {
          const error = await response.json();
          setErrorMessage(error.message || 'Something went wrong. Please contact us.');
          setStatus('error');
          return;
        }
        
        setStatus('success');
      } catch (error) {
        console.error('Error verifying session:', error);
        setStatus('error');
        setErrorMessage('Failed to verify payment status');
      }
    };
    
    verifySession();
  }, [sessionId, router]);

  if (status === 'loading') {
    return (
      <div className="flex h-[70vh] items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="h-8 w-8 animate-spin rounded-full border-b-2 border-primary"></div>
          <p>Confirming payment...</p>
        </div>
      </div>
    );
  }

  if (status === 'not_found') {
    return (
      <div className="flex min-h-[70vh] flex-col items-center justify-center px-4 text-center">
        
        <h1 className="mb-4 text-3xl font-bold">Payment Not Found</h1>
        
        <p className="mb-4 max-w-md text-muted-foreground">
          We couldn't find the payment session you're looking for. This could happen if:
        </p>

        <ul className="mb-8 max-w-md text-left text-muted-foreground">
          <li className="mb-2">• The payment is still processing</li>
          <li className="mb-2">• The session has expired</li>
          <li className="mb-2">• You've used an invalid or outdated payment link</li>
        </ul>

        <div className="flex flex-col gap-3 sm:flex-row">
          <Button asChild>
            <Link href="/pricing">
              Return to Pricing
            </Link>
          </Button>
          
          <Button asChild variant="outline">
            <Link href="/support">
              Contact Support
            </Link>
          </Button>
        </div>
      </div>
    );
  }

  if (status === 'error') {
    return (
      <div className="flex min-h-[70vh] flex-col items-center justify-center px-4 text-center">
        
        <h1 className="mb-4 text-3xl font-bold">Payment Verification Failed</h1>
        
        <p className="mb-8 max-w-md text-muted-foreground">
          {errorMessage || "We encountered an error while verifying your payment. Please contact our support team for assistance."}
        </p>

        <div className="flex flex-col gap-3 sm:flex-row">
          <Button asChild>
            <Link href="/pricing">
              Return to Pricing
            </Link>
          </Button>
          
          <Button asChild variant="outline">
            <Link href="/support">
              Contact Support
            </Link>
          </Button>
        </div>
      </div>
    );
  }
 
  return (
    <div className="flex min-h-[70vh] flex-col items-center justify-center px-4 text-center">
      <h1 className="mb-4 text-3xl font-bold">You are subscribed!</h1>
      
      <p className="mb-8 max-w-md text-muted-foreground">
        Your subscription has been activated. You can now enjoy all the benefits of your selected plan.
      </p>

      <div className="flex flex-col gap-3 sm:flex-row">
        <Button asChild>
          <Link href="/integrations">
            Go to Integrations
          </Link>
        </Button>
        
        <Button asChild variant="outline">
          <Link href="/flows">
            Go to Flows
          </Link>
        </Button>
      </div>
    </div>
  );
} 