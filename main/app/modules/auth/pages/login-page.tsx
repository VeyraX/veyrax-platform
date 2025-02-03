"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { AlertCircle, Loader2 } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { ValidateCredentials, HandleLogin } from "@/lib/actions/actions"

export function LoginForm() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string[]>([]);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const submitLogin = async () => {
    setLoading(true);
    setError([]);
    
    try {
      const isValid = await ValidateCredentials(email, password);
      console.log(email);
      console.log(password);
      console.log(isValid);
      
      if (isValid) {
        await HandleLogin(process.env.NEXT_PUBLIC_AUTH_TOKEN_DATA || '');
        window.location.href = '/assistant';
      } else {
        setError(['Invalid email or password']);
      }
    } catch (error) {
      setError(['An error occurred during login']);
    } finally {
      setLoading(false);
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      submitLogin();
    }
  };

  return (
    <div className="w-full h-screen flex items-center justify-center px-4 md:px-8">
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
          <div className="grid gap-4">
            <div className="grid gap-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="m@example.com"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                onKeyDown={handleKeyPress}
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
                onKeyDown={handleKeyPress}
              />
            </div>
            <Button 
              type="submit" 
              className="w-full" 
              onClick={submitLogin} 
              disabled={loading}
            >
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : "Login"}
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}