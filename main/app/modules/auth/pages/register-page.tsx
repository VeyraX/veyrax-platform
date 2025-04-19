"use client"

import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { AlertCircle, Loader2 } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { authApi } from '@/app/modules/auth/api/api.auth'
import Image from "next/image"
import Link from "next/link"
import Script from "next/script"

export function RegisterForm() {
  const [isEmailLoading, setIsEmailLoading] = useState(false);
  const [isGoogleLoading, setIsGoogleLoading] = useState(false);
  const [isTwitterLoading, setIsTwitterLoading] = useState(false);
  const [error, setError] = useState<string[]>([]);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [turnstileToken, setTurnstileToken] = useState<string | null>(null);
  const turnstileContainerRef = useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    const initTurnstile = () => {
      if (window.turnstile && turnstileContainerRef.current) {
        window.turnstile.render(turnstileContainerRef.current, {
          sitekey: process.env.NEXT_PUBLIC_TURNSTILE_SITE_KEY,
          callback: function(token: string) {
            setTurnstileToken(token);
          },
          'expired-callback': function() {
            setTurnstileToken(null);
          },
          theme: "light"
        });
      }
    };

    // Wait for turnstile to be available
    if (typeof window !== 'undefined') {
      if (window.turnstile) {
        initTurnstile();
      } else {
        window.onloadTurnstileCallback = initTurnstile;
      }
    }

    return () => {
      if (window.turnstile && turnstileContainerRef.current) {
        turnstileContainerRef.current.innerHTML = '';
      }
    };
  }, []);
  
  const handleSignUp = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!turnstileToken) {
      setError(["Please complete the security verification"]);
      return;
    }
    
    setIsEmailLoading(true);
    setError([]);
    
    const { error } = await authApi.register(email, password, turnstileToken);
    if (error) {
      setError([error.message]);
      if (window.turnstile && turnstileContainerRef.current) {
        turnstileContainerRef.current.innerHTML = '';
        window.turnstile.render(turnstileContainerRef.current, {
          sitekey: "0x4AAAAAABPbjRerPp3vmWzm",
          callback: function(token: string) {
            setTurnstileToken(token);
          },
          theme: "light"
        });
      }
    } else {
      window.location.href = '/agent';
    }
    setIsEmailLoading(false);
  };

  const handleGoogleSignUp = async () => {
    setIsGoogleLoading(true);
    setError([]);
    
    const { error } = await authApi.loginWithGoogle();
    if (error) {
      setError([error.message]);
    }
    setIsGoogleLoading(false);
  };

  const handleTwitterSignUp = async () => {
    setIsTwitterLoading(true);
    setError([]);
    
    const { error } = await authApi.loginWithTwitter();
    if (error) {
      setError([error.message]);
    }
    setIsTwitterLoading(false);
  };

  return (
    <>
      <Script 
        src="https://challenges.cloudflare.com/turnstile/v0/api.js?onload=onloadTurnstileCallback&render=explicit" 
        strategy="afterInteractive"
      />
      <div className="w-full flex items-center justify-center px-4 md:px-8">
        <div className="flex items-center justify-center">
          <div className="mx-auto grid w-[350px] gap-6">
            <div className="grid gap-2 text-center">
              <h1 className="text-3xl font-bold tracking-tight">Create an account</h1>
              {error.length > 0 && 
                <Alert variant="destructive" className="mb-4">
                  <div className="flex items-center gap-2">
                    <AlertCircle className="w-4 h-4" />
                    <AlertDescription className="text-sm">{error}</AlertDescription>
                  </div>
                </Alert>
              }
            </div>
            <form onSubmit={handleSignUp} className="grid gap-4">
              <div className="grid gap-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="m@example.com"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="password">Password</Label>
                <Input 
                  id="password" 
                  type="password" 
                  required 
                  value={password} 
                  onChange={(e) => setPassword(e.target.value)} 
                />
              </div>
              
              <div className="w-full flex justify-center">
                <div ref={turnstileContainerRef} className="cf-turnstile" data-theme="light"></div>
              </div>
              
              <Button 
                type="submit" 
                className="w-full" 
                disabled={isEmailLoading || isGoogleLoading || isTwitterLoading || !turnstileToken}
              >
                {isEmailLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : "Sign up"}
              </Button>

              <div className="text-center text-sm text-muted-foreground">
                Already have an account?{" "}
                <Link href="/login" className="text-primary hover:underline">
                  Login
                </Link>
              </div>

              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <span className="w-full border-t" />
                </div>
                <div className="relative flex justify-center text-xs uppercase">
                  <span className="bg-background px-2 text-muted-foreground">
                    Or continue with
                  </span>
                </div>
              </div>

              <Button
                variant="outline"
                type="button"
                onClick={handleGoogleSignUp}
                disabled={isEmailLoading || isGoogleLoading || isTwitterLoading}
                className="flex items-center gap-2"
              >
                {isGoogleLoading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <>
                    <Image 
                      src="/logos/google-logo.svg" 
                      alt="Google logo" 
                      width={16} 
                      height={16} 
                    />
                    <span>Sign up with Google</span>
                  </>
                )}
              </Button>
            </form>
          </div>
        </div>
      </div>
    </>
  )
}

// Declare global window interface with turnstile
declare global {
  interface Window {
    turnstile: {
      render: (container: HTMLElement, options: any) => string;
      reset: (widgetId: string) => void;
    };
    onloadTurnstileCallback: () => void;
  }
}
