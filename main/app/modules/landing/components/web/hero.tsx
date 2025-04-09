"use client";

import { useEffect, useState } from "react";
import { MoveRight, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import Particles from "@/components/ui/particles";
import { useTheme } from "next-themes";
import { BorderBeam } from "@/components/ui/border-beam";
import Link from "next/link";
import Image from "next/image";

export const Hero = () => {
  const { resolvedTheme } = useTheme();
  const [color, setColor] = useState("#ffffff");

  useEffect(() => {
    setColor(resolvedTheme === "dark" ? "#ffffff" : "#000000");
  }, [resolvedTheme]);

  return (
    <div className="w-full">
      <div className="w-full h-full flex flex-col items-center justify-center px-2 md:px-4">
        <div className="flex items-center justify-center py-4 w-full">
          <div className="w-full">
            <div className="flex gap-6 items-center justify-center flex-col relative">
              <Particles
                className="absolute inset-0"
                quantity={100}
                ease={80}
                color={color}
                refresh
              />
              
              <div className="flex gap-4 flex-col mb-2 md:mb-4">
                <Link href="/web/flow" className="self-center">
                  <span className="text-spektr-cyan-50 text-sm md:text-base px-4 py-1.5 rounded-full bg-spektr-cyan-50/10 border border-spektr-cyan-50/20 flex items-center gap-1.5 transition-colors hover:bg-black hover:text-white hover:border-black cursor-pointer group">
                    Introducing VeyraX Flow <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" /> 
                  </span>
                </Link>
                
                <h1 className="text-4xl md:text-6xl max-w-2xl tracking-tighter text-center font-regular">
                  <span className="text-spektr-cyan-50">VeyraX is </span>
                  <span className="font-semibold">Agentic Component Interface</span>
                </h1>

                <p className="text-base md:text-lg leading-relaxed tracking-tight text-muted-foreground max-w-2xl text-center">
                  We seamlessly integrate both UI and API of 50+ tools, enabling AI Agents to connect to any system in just one line of code.
                </p>
              </div>
              
              <div className="flex flex-row items-center gap-4 w-full max-w-md justify-center mb-2 md:mb-4">
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

              <div className="relative w-full max-w-[95vw] z-10">
                <div className="relative w-full border border-border rounded-xl overflow-hidden">
                  <BorderBeam size={450} duration={12} delay={9} />
                  <div className="w-full aspect-[21/9] md:aspect-[21/9] lg:aspect-[21/8] xl:h-[70vh] relative">
                    <Image 
                      src="/landing/hero_web.png"
                      alt="VeyraX Marketplace"
                      fill
                      className="object-cover"
                      priority
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};