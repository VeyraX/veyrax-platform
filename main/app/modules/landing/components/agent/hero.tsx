"use client";

import { useEffect, useMemo, useState } from "react";
import { MoveRight, PhoneCall, ArrowUp } from "lucide-react";
import { Button } from "@/components/ui/button";
import Particles from "@/components/ui/particles";
import { useTheme } from "next-themes";
import { BorderBeam } from "@/components/ui/border-beam";
import HeroVideoDialog from "@/components/ui/hero-video-dialog";
import { Input } from "@/components/ui/input";
import { WaitlistService } from '../../api/api.service';
import { Alert, AlertDescription } from "@/components/ui/alert";
import { validateEmail } from '@/lib/utils/email-validator';
import { AnimatedTooltip } from "./animated-tooltip";
import { TypewriterEffect } from "./typewirter-effect";
import { BetaDialog } from './beta-dialog';

export const Hero = () => {
  const { resolvedTheme } = useTheme();
  const [color, setColor] = useState("#ffffff");
  const [titleNumber, setTitleNumber] = useState(0);
  const [email, setEmail] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);
  const [showForm, setShowForm] = useState(true);
  const [avatarData] = useState([
    {
      id: 1,
      name: "Gmail",
      designation: "Email Client",
      image: "/logos/gmail-logo.svg"
    },
    {
      id: 2,
      name: "Perplexity",
      designation: "AI Search",
      image: "/logos/perplexity-logo.svg"
    },
    {
      id: 3,
      name: "Linear",
      designation: "Project Management",
      image: "/logos/linear-logo.svg"
    },
    {
      id: 4,
      name: "Notion",
      designation: "Workspace",
      image: "/logos/notion-logo.svg"
    },
    {
      id: 5,
      name: "Slack",
      designation: "Communication",
      image: "/logos/slack-logo.svg"
    },
    {
      id: 6,
      name: "X",
      designation: "Social Media",
      image: "/logos/x-logo.svg"
    },
    {
      id: 7,
      name: "X",
      designation: "Communication",
      image: "/logos/x-logo.svg"
    }
  ]);

  const typewriterTexts = useMemo(() => [
    "search my emails...",
    "schedule meeting with...",
    "create task about...",
    "find documents...",
    "read recent notifications from...",
    "follow up leads about...",
    "analyze files...",
    "reply in chats with...",
    "search web for...",
    "check weather in..."
  ], []);

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
              <div className="flex flex-col gap-1 items-center">
                <div>
                  <AnimatedTooltip items={avatarData} numPeople={20} />
                </div>
                <h1 className="text-5xl md:text-7xl max-w-2xl tracking-tighter text-center font-regular">
                  <div>
                    <span className="text-spektr-cyan-50">All your favorite tools</span>
                  </div>
                  <div>
                    <span className="font-semibold">with power of AI</span>
                  </div>
                </h1>
              </div>

              <p className="text-lg md:text-xl leading-relaxed tracking-tight text-muted-foreground max-w-2xl text-center">
                Use power of AI Agents with your favorite tools. Explore data, ask questions, and execute actions.{" "}
              </p>
              <div className="relative w-full max-w-xl">
                <div className="w-full border border-black/10 dark:border-white/10 rounded-xl shadow-sm">
                  <div className="w-full rounded-xl px-4 py-3 bg-black/5 dark:bg-white/5">
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-muted-foreground">
                        <TypewriterEffect texts={typewriterTexts} />
                      </span>
                      <BetaDialog 
                        trigger={
                          <Button
                            variant="outline"
                            className="rounded-full transition-all duration-200 ease-in-out border-0 relative overflow-hidden hover:bg-black/5 dark:hover:bg-white/5"
                          >
                            Join Beta
                            <ArrowUp className="w-4 h-4 relative z-10" />
                          </Button>
                        }
                      />
                    </div>
                  </div>
                </div>
              </div> 

              <div className="relative w-full max-w-7xl z-10">
                <div className="relative w-full border border-border rounded-xl overflow-hidden">
                  <BorderBeam size={350} duration={12} delay={9} />
                  <HeroVideoDialog
                    className="dark:hidden block"
                    animationStyle="from-center"
                    videoSrc="https://www.youtube.com/embed/MjuEsZ650y8"
                    thumbnailSrc="/landing/hero_video_beta.png"
                    thumbnailAlt="Hero Video"
                  />
                  <HeroVideoDialog
                    className="hidden dark:block"
                    animationStyle="from-center"
                    videoSrc="https://www.youtube.com/embed/MjuEsZ650y8"
                    thumbnailSrc="/landing/hero_video_beta.png"
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