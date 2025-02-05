"use client";

import { useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import { MoveRight, PhoneCall } from "lucide-react";
import { Button } from "@/components/ui/button";
import Particles from "@/components/ui/particles";
import { useTheme } from "next-themes";
import { BorderBeam } from "@/components/ui/border-beam";

export const Hero = () => {
  const { resolvedTheme } = useTheme();
  const [color, setColor] = useState("#ffffff");
  const [titleNumber, setTitleNumber] = useState(0);
  
  const titles = useMemo(
    () => [
      "Agenic UI Components",
      "Unified API for any software",
      "Agentic Component Interface",
    ],
    []
  );


  useEffect(() => {
    setColor(resolvedTheme === "dark" ? "#ffffff" : "#000000");
  }, [resolvedTheme]);

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (titleNumber === titles.length - 1) {
        setTitleNumber(0);
      } else {
        setTitleNumber(titleNumber + 1);
      }
    }, 2000);
    return () => clearTimeout(timeoutId);
  }, [titleNumber, titles]);

  return (
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
                <span className="text-spektr-cyan-50">VeryaX is </span>
                <span className="font-semibold">Agenic Component Interface</span>
              </h1>

              <p className="text-lg md:text-xl leading-relaxed tracking-tight text-muted-foreground max-w-2xl text-center">
                We seamlessly integrate both UI components and API interfaces, enabling AI Agents to effortlessly connect with any system.
              </p>
            </div>
            <div className="flex flex-row gap-3">
              <Button
                size="lg"
                className="gap-4"
                variant="outline"
                asChild
              >
                <a
                  href="https://forms.gle/UhpZG86ykSgVnsKy8"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Get a demo <PhoneCall className="w-4 h-4" />
                </a>
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
                  className="w-full h-auto -mt-[1px] md:-mb-[130px]"
                >
                  <source src="/landing/hero_video.mp4" type="video/mp4" />
                </video>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};