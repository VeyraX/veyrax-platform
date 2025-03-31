"use client";

import { useEffect, useState } from "react";
import { MoveRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import Particles from "@/components/ui/particles";
import { useTheme } from "next-themes";
import { BorderBeam } from "@/components/ui/border-beam";
import Image from "next/image";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import { authApi } from '@/app/modules/auth/api/api.auth';
import { useRouter } from 'next/navigation';
import { getUserProfile } from '@/app/modules/settings/api/api.settings';
import { UserProfile } from '@/app/modules/settings/api/types.settings';

interface ClickIconProps {
  x: number;
  y: number;
  onComplete: () => void;
  delay: number;
}

const ClickIcon = ({ x, y, onComplete, delay }: ClickIconProps) => {
  const [clickCount, setClickCount] = useState(0);
  const [position, setPosition] = useState({ x, y });

  useEffect(() => {
    let clicks = 0;
    const maxClicks = 5;
    const clickSound = new Audio('/click.mp3');

    const performClick = () => {
      clickSound.currentTime = 0;
      clickSound.play();
      setClickCount(prev => prev + 1);
      clicks++;

      // Random movement after each click with larger range
      setPosition(prev => ({
        x: prev.x + (Math.random() * 150 - 75),
        y: prev.y + (Math.random() * 90 - 45)
      }));

      if (clicks < maxClicks) {
        setTimeout(performClick, Math.random() * 800 + 400);
      } else {
        setTimeout(onComplete, 1000);
      }
    };

    setTimeout(performClick, delay);

    return () => {
      clickSound.pause();
      clickSound.currentTime = 0;
    };
  }, [onComplete, delay]);

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0 }}
      animate={{ 
        opacity: 1, 
        scale: 1.5,
        x: position.x,
        y: position.y,
        transition: { type: "spring", damping: 8, duration: 0.5 }
      }}
      className="absolute"
      style={{ left: -12, top: -12 }}
    >
      <motion.div
        animate={{
          scale: [1, 0.8, 1],
        }}
        transition={{
          duration: 0.3,
          times: [0, 0.5, 1],
          repeat: clickCount
        }}
      >
        <Image
          src="/mouse-click-icon.svg"
          width={36}
          height={36}
          alt="Click"
        />
      </motion.div>
    </motion.div>
  );
};

export const Hero = () => {
  const { resolvedTheme } = useTheme();
  const [color, setColor] = useState("#ffffff");
  const [clicks, setClicks] = useState<{ id: number; x: number; y: number; delay: number }[]>([]);
  const [clickCount, setClickCount] = useState(0);
  const router = useRouter();
  const [isGoogleLoading, setIsGoogleLoading] = useState(false);
  const [profile, setProfile] = useState<UserProfile | null>(null);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const data = await getUserProfile();
        setProfile(data);
      } catch (error) {
        console.error('Error fetching user profile:', error);
      }
    };
    
    fetchProfile();
  }, []);

  useEffect(() => {
    setColor(resolvedTheme === "dark" ? "#ffffff" : "#000000");
  }, [resolvedTheme]);

  const handleZapierClick = () => {
    const newClicks: Array<{ id: number; x: number; y: number; delay: number }> = [];
    for (let i = 0; i < 15; i++) {
      const randomX = Math.random() * window.innerWidth;
      const randomY = Math.random() * window.innerHeight;
      newClicks.push({
        id: clickCount + i,
        x: randomX,
        y: randomY,
        delay: Math.random() * 500
      });
    }
    setClicks(prev => [...prev, ...newClicks]);
    setClickCount(prev => prev + 15);
  };

  const removeClick = (id: number) => {
    setClicks(prev => prev.filter(click => click.id !== id));
  };

  const handleEmailSignUp = () => {
    if (profile) {
      router.push('/flows');
    } else {
      router.push('/register');
    }
  };

  const handleGoogleSignUp = async () => {
    if (profile) {
      router.push('/flows');
      return;
    }

    setIsGoogleLoading(true);
    const { error } = await authApi.loginWithGoogle();
    if (error) {
      console.error('Google sign-up error:', error);
    } else {
      window.location.href = '/flows';
    }
    setIsGoogleLoading(false);
  };

  return (
    <div className="w-full pt-8">
      <AnimatePresence>
        {clicks.map(click => (
          <ClickIcon
            key={click.id}
            x={click.x}
            y={click.y}
            delay={click.delay}
            onComplete={() => removeClick(click.id)}
          />
        ))}
      </AnimatePresence>
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
                  <h1 className="text-5xl md:text-7xl max-w-3xl tracking-tighter text-center font-bold">
                    Imagine... like <span className="text-orange-500 cursor-pointer hover:opacity-80 transition-opacity" onClick={handleZapierClick}>Zapier</span>, but without clicking...
                  </h1>
                </div>

                <p className="text-lg md:text-xl leading-relaxed tracking-tight text-muted-foreground max-w-2xl text-center">
                    VeyraX Flow is AI-powered automation where you can create, run and schedule workflows with just natural language.
                </p>
              </div>

              <div className="flex flex-row items-center gap-4 w-full max-w-md justify-center">
                <Button 
                  className="gap-2"
                  onClick={handleEmailSignUp}
                >
                  {profile ? 'Go to Flows' : 'Sign up with email'}
                </Button>
                
                <Button 
                  variant="outline" 
                  className="flex items-center gap-2"
                  onClick={handleGoogleSignUp}
                  disabled={isGoogleLoading}
                >
                  <Image 
                    src="/logos/google-logo.svg" 
                    alt="Google logo" 
                    width={16} 
                    height={16} 
                  />
                  <span>{profile ? 'Go to Flows' : 'Sign up with Google'}</span>
                </Button>
              </div>

              <div className="relative w-full max-w-7xl z-10">
                <div className="relative w-full border border-border rounded-xl overflow-hidden">
                  <BorderBeam size={350} duration={12} delay={9} />
                  <video
                    autoPlay
                    muted
                    loop
                    playsInline
                    className="w-full h-auto"
                  >
                    <source src="/flow_video/video_demo.mp4" type="video/mp4" />
                  </video>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};