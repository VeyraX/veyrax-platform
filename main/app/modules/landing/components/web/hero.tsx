"use client";

import { useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import { MoveRight, PhoneCall } from "lucide-react";
import { Button } from "@/components/ui/button";
import Particles from "@/components/ui/particles";
import { useTheme } from "next-themes";
import { BorderBeam } from "@/components/ui/border-beam";
import HeroVideoDialog from "@/components/ui/hero-video-dialog";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { WaitlistService } from '../../api/api.service';
import { Alert, AlertDescription } from "@/components/ui/alert";
import { validateEmail } from '@/lib/utils/email-validator';

export const Hero = () => {
  const { resolvedTheme } = useTheme();
  const [color, setColor] = useState("#ffffff");
  const [titleNumber, setTitleNumber] = useState(0);
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
    <div className="w-full pt-8">
      <div className="w-full h-full flex items-center justify-center px-4 md:px-8">
        <div className="flex items-center justify-center py-6">
          <div className="container mx-auto">
            <div className="flex gap-8 py-8 lg:py-16 items-center justify-center flex-col relative">
              <Particles
                className="absolute inset-0"
                quantity={100}
                ease={80}
                color={color}
                refresh
              />
              
              <div className="flex gap-4 flex-col">
                <h1 className="text-5xl md:text-7xl max-w-2xl tracking-tighter text-center font-regular">
                  <span className="text-spektr-cyan-50">VeyraX is </span>
                  <span className="font-semibold">Agentic Component Interface</span>
                </h1>

                <p className="text-lg md:text-xl leading-relaxed tracking-tight text-muted-foreground max-w-2xl text-center">
                  We seamlessly integrate both UI components and API interfaces, enabling AI Agents to effortlessly connect with any system.
                </p>
              </div>
              
              <div className="flex flex-col items-center gap-4 w-full max-w-md">
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

              <div className="relative w-full max-w-7xl z-10">
                <div className="relative w-full border border-border rounded-xl overflow-hidden">
                  <BorderBeam size={350} duration={12} delay={9} />
                  <HeroVideoDialog
                    className="dark:hidden block"
                    animationStyle="from-center"
                    videoSrc="https://www.youtube.com/embed/i7bNafDInRA?si=4rb-zSdDkVK9qxxb"
                    thumbnailSrc="/landing/hero_video.png"
                    thumbnailAlt="Hero Video"
                  />
                  <HeroVideoDialog
                    className="hidden dark:block"
                    animationStyle="from-center"
                    videoSrc="https://www.youtube.com/embed/i7bNafDInRA?si=4rb-zSdDkVK9qxxb"
                    thumbnailSrc="/landing/hero_video.png"
                    thumbnailAlt="Hero Video"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};