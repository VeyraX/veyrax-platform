"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { AlertCircle, Loader2 } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { authApi } from '@/app/modules/auth/api/api.auth'
import Image from "next/image"

export function RegisterForm() {
  const [isEmailLoading, setIsEmailLoading] = useState(false);
  const [isGoogleLoading, setIsGoogleLoading] = useState(false);
  const [isTwitterLoading, setIsTwitterLoading] = useState(false);
  const [error, setError] = useState<string[]>([]);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  
  const handleSignUp = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsEmailLoading(true);
    setError([]);
    
    const { error } = await authApi.register(email, password);
    if (error) {
      setError([error.message]);
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
            <Button 
              type="submit" 
              className="w-full" 
              disabled={isEmailLoading || isGoogleLoading || isTwitterLoading}
            >
              {isEmailLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : "Sign up"}
            </Button>

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
  )
}
