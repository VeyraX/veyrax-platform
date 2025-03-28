"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { AlertCircle, Loader2 } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import Link from "next/link"
import { createClient } from '@/lib/utils/supabase/client'
import { authApi } from '../api/api.auth'
import Image from "next/image"

export function LoginForm() {
  const [isEmailLoading, setIsEmailLoading] = useState(false);
  const [isGoogleLoading, setIsGoogleLoading] = useState(false);
  const [isTwitterLoading, setIsTwitterLoading] = useState(false);
  const [error, setError] = useState<string[]>([]);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsEmailLoading(true);
    setError([]);
    
    const { error } = await authApi.login(email, password);
    if (error) {
      if (error.message.includes('Invalid login credentials')) {
        setError(['Invalid email or password. Please try again.']);
      } else {
        setError([error.message]);
      }
    } else {
      window.location.href = '/agent/new';
    }
    setIsEmailLoading(false);
  };

  const handleGoogleLogin = async () => {
    setIsGoogleLoading(true);
    setError([]);
    
    const { error } = await authApi.loginWithGoogle();
    if (error) {
      setError([error.message]);
    }
    setIsGoogleLoading(false);
  };

  const handleTwitterLogin = async () => {
    setIsTwitterLoading(true);
    setError([]);
    
    const { error } = await authApi.loginWithTwitter();
    if (error) {
      setError([error.message]);
    }
    setIsTwitterLoading(false);
  };

  return (
    <div className="w-full flex items-center justify-center px-4 md:px-8">
      <div className="flex items-center justify-center">
        <div className="mx-auto grid w-[350px] gap-6">
          <div className="grid gap-2 text-center">
            <h1 className="text-3xl font-bold tracking-tight">Welcome back</h1>
            {error.length > 0 && 
              <Alert variant="destructive" className="mb-4">
                <div className="flex items-center gap-2">
                  <AlertCircle className="w-4 h-4" />
                  <AlertDescription className="text-sm">{error}</AlertDescription>
                </div>
              </Alert>
            }
          </div>
          <form onSubmit={handleSubmit} className="grid gap-4">
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
            
            <Button 
              type="submit" 
              className="w-full" 
              disabled={isEmailLoading || isGoogleLoading || isTwitterLoading}
            >
              {isEmailLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : "Login"}
            </Button>

            <div className="text-center text-sm text-muted-foreground">
              Don't have an account?{" "}
              <Link href="/register" className="text-primary hover:underline">
                Sign Up
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
              onClick={handleGoogleLogin}
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
                  <span>Sign in with Google</span>
                </>
              )}
            </Button>
          </form>
        </div>
      </div>
    </div>
  )
}