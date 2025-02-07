'use client';

import { FC, forwardRef, useRef, useEffect, useState } from 'react';
import { cn } from '@/lib/utils';
import { useTheme } from 'next-themes';
import { AnimatedBeam } from "@/components/ui/animated-beam";
import NotionLogo from '@/public/logos/notion-logo.svg';
import GoogleCalendarLogo from '@/public/logos/google-calendar-logo.svg';
import Image from 'next/image';
import { motion } from "framer-motion";
import { User, Bot } from "lucide-react";
import AirbnbIcon from '@/public/logos/airbnb-logo.svg';
import PaypalLogo from '@/public/logos/paypal-logo.svg';
import SpotifyLogo from '@/public/logos/spotify-logo.svg';
import AILogo from '@/public/landing/ai.svg';
import Particles from "@/components/ui/particles";


interface TextBlockProps {
  className?: string;
}

const Circle = forwardRef<
  HTMLDivElement,
  { className?: string; children?: React.ReactNode }
>(({ className, children }, ref) => {
  return (
    <div
      ref={ref}
      className={cn(
        "z-10 flex h-24 w-24 items-center justify-center rounded-full border-2 bg-white p-3 shadow-[0_0_20px_-12px_rgba(0,0,0,0.8)]",
        className,
      )}
    >
      {children}
    </div>
  );
});

Circle.displayName = "Circle";

export const TextBlock: FC<TextBlockProps> = ({ className }) => {
  const { resolvedTheme } = useTheme();
  const [color, setColor] = useState("#ffffff");
  
  useEffect(() => {
    setColor(resolvedTheme === "dark" ? "#ffffff" : "#000000");
  }, [resolvedTheme]);

  const containerRef = useRef<HTMLDivElement>(null);
  const service1Ref = useRef<HTMLDivElement>(null);
  const service2Ref = useRef<HTMLDivElement>(null);
  const service3Ref = useRef<HTMLDivElement>(null);
  const service4Ref = useRef<HTMLDivElement>(null);
  const service5Ref = useRef<HTMLDivElement>(null);
  const centerRef = useRef<HTMLDivElement>(null);
  const aiRef = useRef<HTMLDivElement>(null);

  return (
    <section 
      id="text-block"
      className={cn('relative w-full', className)}
    >
      <div className="container mx-auto px-4">
        <div className="mx-auto max-w-4xl space-y-4 relative">
          <Particles
            className="absolute inset-0"
            quantity={100}
            ease={80}
            color={color}
            refresh
          />
          <div className="mx-auto max-w-4xl space-y-4">
            <h2 className="text-5xl md:text-7xl tracking-tighter text-center">
              <span className="font-normal">Introducing</span>{" "}
              <span className="font-bold">ACI</span>
            </h2>
            
            <h3 className="text-lg md:text-xl leading-relaxed tracking-tight text-muted-foreground text-center">
              Agentic Component Interface
            </h3>

            <div className="text-lg md:text-xl leading-relaxed tracking-tight space-y-6 text-center">
              <div className="space-y-6">
                <p className="text-muted-foreground">
                  In the coming years, we envision all web interactions taking place through
                  Super Assistants, fundamentally transforming how we navigate the digital
                  landscape.
                </p>

                <p className="text-muted-foreground">
                  As AI agents become more prevalent, they require both APIs and UI
                  components for seamless user interaction. The future of business isn't
                  about building traditional websites or apps—it's about creating MCP
                  tools and UI Forms that Super Assistants can easily integrate and utilize.
                </p>

                <p className="text-muted-foreground">
                  VeyraX bridges this gap by combining both: providing unified API and UI
                  components designed for seamless integration into any Agentic system.
                </p>
              </div>
            </div>

            <div 
              ref={containerRef}
              className="relative w-full items-center justify-center hidden md:flex"
            >
              <div className="relative h-[600px] w-full flex items-center justify-center overflow-hidden">
                <AnimatedBeam containerRef={containerRef} fromRef={service1Ref} toRef={centerRef} />
                <AnimatedBeam containerRef={containerRef} fromRef={service2Ref} toRef={centerRef} />
                <AnimatedBeam containerRef={containerRef} fromRef={service3Ref} toRef={centerRef} />
                <AnimatedBeam containerRef={containerRef} fromRef={service4Ref} toRef={centerRef} />
                <AnimatedBeam containerRef={containerRef} fromRef={service5Ref} toRef={centerRef} />
                <AnimatedBeam containerRef={containerRef} fromRef={centerRef} toRef={aiRef} />

                <div className="flex w-full flex-col items-center gap-24">
                  <div className="flex gap-12 justify-center">
                    <Circle ref={service1Ref}>
                      <Image src={AirbnbIcon} alt="Airbnb" className="h-10 w-10" />
                    </Circle>
                    <Circle ref={service2Ref}>
                      <Image src={NotionLogo} alt="Notion" className="h-10 w-10" />
                    </Circle>
                    <Circle ref={service3Ref}>
                      <Image src={PaypalLogo} alt="Paypal" className="h-10 w-10" />
                    </Circle>
                    <Circle ref={service4Ref}>
                      <Image src={SpotifyLogo} alt="Spotify" className="h-10 w-10" />
                    </Circle>
                    <Circle ref={service5Ref}>
                      <Image src={GoogleCalendarLogo} alt="Calendar" className="h-10 w-10" />
                    </Circle>
                  </div>

                  {/* Центр - ACI */}
                  <Circle ref={centerRef} className="size-28">
                    <div className="text-2xl font-bold">ACI</div>
                  </Circle>

                  {/* Нижний элемент - AI */}
                  <Circle ref={aiRef} className="size-28">
                    <Image src={AILogo} alt="AI" className="h-12 w-12" />
                  </Circle>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};