"use client";

import { useEffect, useState, useRef } from "react";
import { MoveRight, ArrowRight } from "lucide-react";
import { CalendarIcon, FileTextIcon } from "@radix-ui/react-icons";
import { Button } from "@/components/ui/button";
import Particles from "@/components/ui/particles";
import { useTheme } from "next-themes";
import Link from "next/link";
import Image from "next/image";
import { cn } from "@/lib/utils";
import { BentoCard, BentoGrid } from "@/components/ui/bento-grid";
import { ConnectIcon as Connect } from "@/components/ui/connect";
import { LayersIcon as Layers } from "@/components/ui/layers";
import { CompassIcon as Compass } from "@/components/ui/compass";
import { FingerprintIcon as Fingerprint } from "@/components/ui/fingerprint";

export const HeroNew = () => {
  const { resolvedTheme } = useTheme();
  const [color, setColor] = useState("#ffffff");

  useEffect(() => {
    setColor(resolvedTheme === "dark" ? "#ffffff" : "#000000");
  }, [resolvedTheme]);

  const features = [
    {
      Icon: Connect,
      name: "Integrations & MCPs",
      description: "Connect your Agent to 100+ tools and 3000+ MCPs seamlessly.",
      href: "/mcp",
      cta: "Learn more",
      className: "col-span-6 md:col-span-4 min-h-[280px] relative overflow-hidden",
      background: (
        <div className="absolute inset-0 flex items-center justify-end">
          <div className="absolute right-[-20%] top-[5%] w-[80%] h-[90%] opacity-75 rounded-2xl overflow-hidden">
            <div className="relative w-full h-full">
              <Image 
                src="/landing/hero/tools.png" 
                alt="VeyraX Tools" 
                fill 
                className="object-cover rounded-2xl"
                style={{ objectPosition: '40% 20%' }}
              />
              <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-background/90 pointer-events-none" />
            </div>
          </div>
        </div>
      ),
    },
    {
      Icon: Compass,
      name: "Memory",
      description: "Retain information automatically based on all user requests.",
      href: "/web/memory",
      cta: "Learn more",
      className: "col-span-6 md:col-span-2 min-h-[280px] relative overflow-hidden",
      background: (
        <div className="absolute inset-0 flex items-center justify-end">
          <div className="absolute right-[-10%] top-[2%] w-[95%] h-[95%] opacity-75 rounded-2xl overflow-hidden">
            <div className="relative w-full h-full">
              <Image 
                src="/landing/hero/memory.png" 
                alt="VeyraX Memory" 
                fill 
                className="object-cover rounded-2xl"
                style={{ objectPosition: '-20% top' }}
              />
              <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-background/90 pointer-events-none" />
            </div>
          </div>
        </div>
      ),
    },
    {
      Icon: Fingerprint,
      name: "Auth",
      description: "Authenticate your users with VeyraX integrations and MCPs.",
      href: "#",
      cta: "Soon...",
      className: "col-span-6 md:col-span-2 min-h-[280px] relative overflow-hidden",
      background: (
        <div className="absolute inset-0 flex items-center justify-end">
          <div className="absolute right-[-10%] top-[2%] w-[95%] h-[95%] opacity-75 rounded-2xl overflow-hidden">
            <div className="relative w-full h-full">
              <Image 
                src="/landing/hero/auth.png" 
                alt="VeyraX Auth" 
                fill 
                className="object-cover rounded-2xl"
                style={{ objectPosition: '-20% top' }}
              />
              <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-background/90 pointer-events-none" />
            </div>
          </div>
        </div>
      ),
    },
    {
      Icon: Layers,
      name: "Flow",
      description: "Agent-powered tools execution workflows.",
      className: "col-span-6 md:col-span-4 min-h-[280px] relative overflow-hidden",
      href: "/web/flow",
      cta: "Learn more",
      background: (
        <div className="absolute inset-0 flex items-center justify-end">
          <div className="absolute right-[-20%] top-[5%] w-[80%] h-[90%] opacity-75 rounded-2xl overflow-hidden">
            <div className="relative w-full h-full">
              <Image 
                src="/landing/hero/flow.png" 
                alt="VeyraX Flow" 
                fill 
                className="object-cover rounded-2xl"
                style={{ objectPosition: '40% 20%' }}
              />
              <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-background/90 pointer-events-none" />
            </div>
          </div>
        </div>
      ),
    },
  ];

  return (
    <div className="w-full">
      <div className="w-full h-full flex flex-col items-center justify-center px-2 md:px-4">
        <div className="flex items-center justify-center py-4 w-full">
          <div className="w-full">
            <div className="flex gap-6 items-center justify-center flex-col relative">
              <Particles
                className="absolute inset-0 -z-10"
                quantity={100}
                ease={80}
                color={color}
                refresh
              />
              
              <div className="flex gap-4 flex-col mb-2 md:mb-4 mt-16 md:mt-24 items-center">
                
                <h1 className="text-4xl md:text-6xl max-w-2xl tracking-tighter text-center font-regular">
                  <span className="font-semibold block">Infrastructure Layer</span>
                  <span className="font-semibold block">for AI Agents</span>
                </h1>

                <p className="text-base md:text-lg leading-relaxed tracking-tight text-muted-foreground max-w-2xl text-center">
                  We provide the complete foundation for AI Agents with essential capabilities they need — memory, authentication, workflows, and everything in between.
                </p>
              </div>
              
              <div className="flex flex-row items-center gap-4 w-full max-w-md justify-center mb-8 md:mb-12">
                <Link href="/register">
                  <Button className="gap-2">
                    Register <MoveRight className="w-4 h-4" />
                  </Button>
                </Link>
                
                <Link href="/marketplace">
                  <Button variant="outline" className="gap-2">
                    Explore Marketplace
                  </Button>
                </Link>
              </div>

              <div className="w-full max-w-6xl px-4">
                <div className="grid grid-cols-6 gap-4 md:gap-6">
                  {features.map((feature, idx) => (
                    <BentoCard key={idx} {...feature} />
                  ))}
                </div>
              </div>

            </div>
          </div>
        </div>
      </div>
    </div>
  );
};