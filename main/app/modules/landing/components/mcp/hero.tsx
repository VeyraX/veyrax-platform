"use client";

import { useEffect, useState } from "react";
import { MoveRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import Particles from "@/components/ui/particles";
import { useTheme } from "next-themes";
import { BorderBeam } from "@/components/ui/border-beam";
import HeroVideoDialog from "@/components/ui/hero-video-dialog";
import { Input } from "@/components/ui/input";
import { WaitlistService } from '../../api/api.service';
import { Alert, AlertDescription } from "@/components/ui/alert";
import { validateEmail } from '@/lib/utils/email-validator';
import { WaitlistDialog } from "../web/waitlist-dialog";
import Link from "next/link";

export const Hero = () => {
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
    <div className="w-full pt-8">
      <div className="w-full h-full flex items-center justify-center px-4 md:px-8">
        <div className="flex items-center justify-center py-8 md:py-16">
          <div className="container mx-auto">
            <div className="flex gap-8 items-center justify-center flex-col relative">
              <Particles
                className="absolute inset-0"
                quantity={100}
                ease={80}
                color={color}
                refresh
              />
              
              <div className="flex gap-4 flex-col items-center">
                <div className="flex flex-col items-center gap-3">
                  <span className="text-spektr-cyan-50 text-sm md:text-base px-4 py-1.5 rounded-full bg-spektr-cyan-50/10 border border-spektr-cyan-50/20 flex items-center gap-1.5 transition-colors hover:bg-black hover:text-white hover:border-black cursor-pointer">
                    VeyraX MCP
                  </span>
                  <h1 className="text-5xl md:text-7xl max-w-2xl tracking-tighter text-center font-regular">
                    <div>
                      <div><span className="font-semibold">Single tool</span> to control</div>
                      <div>them all</div>
                    </div>
                  </h1>
                </div>

                <p className="text-lg md:text-xl leading-relaxed tracking-tight text-muted-foreground max-w-2xl text-center">
                  VeyraX MCP is a only connection you need to get access to all your tools in any MCP-compatible environments.{" "}
                </p>
              </div>

              <div className="flex flex-row items-center gap-4 w-full max-w-md justify-center">
                <WaitlistDialog 
                  trigger={
                    <Button className="gap-2">
                      Join Waitlist <MoveRight className="w-4 h-4" />
                    </Button>
                  } 
                />
                
                <Link href="https://docs.veyrax.com/mcp" target="_blank" rel="noopener noreferrer">
                  <Button variant="outline">
                    Explore Docs
                  </Button>
                </Link>
              </div>

              <div className="relative w-full max-w-7xl z-10">
                <div className="relative w-full border border-border rounded-xl overflow-hidden">
                  <BorderBeam size={350} duration={12} delay={9} />
                  <HeroVideoDialog
                    className="dark:hidden block"
                    animationStyle="from-center"
                    videoSrc="https://www.youtube.com/embed/f46EsOCF7fg"
                    thumbnailSrc="/landing/hero_mcp.png"
                    thumbnailAlt="Hero Video"
                  />
                  <HeroVideoDialog
                    className="hidden dark:block"
                    animationStyle="from-center"
                    videoSrc="https://www.youtube.com/embed/f46EsOCF7fg"
                    thumbnailSrc="/landing/hero_mcp.png"
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