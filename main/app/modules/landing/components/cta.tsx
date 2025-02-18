"use client";
import { Button } from "@/components/ui/button";
import Particles from "@/components/ui/particles";
import { useTheme } from "next-themes";
import { useEffect, useState } from "react";
import Link from "next/link";
import { WaitlistDialog } from "../components/waitlist-dialog"
import { MoveRight } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Input } from "@/components/ui/input";
import { WaitlistService } from "../api/waitlist.service";
import { validateEmail } from '@/lib/utils/email-validator';

export const CTA = () => {
  const { resolvedTheme } = useTheme();
  const [color, setColor] = useState("#ffffff");
  const [email, setEmail] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);
  const [showForm, setShowForm] = useState(true);

  useEffect(() => {
    setColor(resolvedTheme === "dark" ? "#ffffff" : "#000000");
  }, [resolvedTheme]);

  useEffect(() => {
    if (message?.type === 'error') {
      const timer = setTimeout(() => {
        setMessage(null);
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [message]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setMessage(null);

    if (!validateEmail(email)) {
      setMessage({
        type: 'error',
        text: 'Please enter a valid email address'
      });
      setIsLoading(false);
      return;
    }

    const result = await WaitlistService.addToWaitlist(email);
    
    setMessage({
      type: result.data ? 'success' : 'error',
      text: result.data 
        ? "You've been added to the waitlist. We'll be in touch soon!"
        : result.error.message.includes('unique constraint') 
          ? "This email is already on the waitlist. We'll be in touch soon!"
          : result.error.message
    });

    if (result.data) {
      setEmail('');
      setShowForm(false);
    }
    
    setIsLoading(false);
  };

  return (
    <div className="w-full">
      <div className="container mx-auto">
        <div className="flex flex-col items-center text-center relative">
          <Particles
            className="absolute inset-0"
            quantity={100}
            ease={80}
            color={color}
            refresh
          />
          <div className="flex flex-col items-center text-center pb-24">
            <div className="flex gap-4 flex-col">
              <h1 className="text-5xl md:text-7xl max-w-2xl tracking-tighter font-regular">
                <span className="text-spektr-cyan-50">AI Agents</span>{" "}
                <span className="font-semibold">will eat the web</span>
              </h1>
              <p className="text-lg md:text-xl leading-relaxed tracking-tight text-muted-foreground max-w-2xl">
                Everything will be consilated and tools integration is last bottleneck. We will try our best to help it do so.
              </p>
            </div>
            <div className="flex flex-col items-center gap-4 w-full max-w-md mt-8">
              {message && (
                <Alert variant={message.type === 'success' ? 'default' : 'destructive'} className="w-full">
                  <AlertDescription className="text-center">
                    {message.text}
                  </AlertDescription>
                </Alert>
              )}
              
              {showForm && (
                <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3 w-full">
                  <Input
                    type="email"
                    placeholder="Enter your email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    className="flex-1 px-4 py-2 rounded-lg border border-border bg-background"
                  />
                  <Button type="submit" disabled={isLoading} className="gap-2">
                    {isLoading ? 'Joining...' : 'Join Waitlist'} <MoveRight className="w-4 h-4" />
                  </Button>
                </form>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
