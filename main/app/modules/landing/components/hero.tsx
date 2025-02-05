"use client";

import { useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import { MoveRight, PhoneCall } from "lucide-react";
import { Button } from "@/components/ui/button";
import Particles from "@/components/ui/particles";
import { useTheme } from "next-themes";
import { BorderBeam } from "@/components/ui/border-beam";
import HeroVideoDialog from "@/components/ui/hero-video-dialog";

export const Hero = () => {
  const { resolvedTheme } = useTheme();
  const [color, setColor] = useState("#ffffff");
  const [titleNumber, setTitleNumber] = useState(0);


  useEffect(() => {
    setColor(resolvedTheme === "dark" ? "#ffffff" : "#000000");
  }, [resolvedTheme]);

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
                  <HeroVideoDialog
                    className="dark:hidden block"
                    animationStyle="from-center"
                    videoSrc="https://www.youtube.com/embed/qh3NGpYRG3I?si=4rb-zSdDkVK9qxxb"
                    thumbnailSrc="https://startup-template-sage.vercel.app/hero-light.png"
                    thumbnailAlt="Hero Video"
                  />
                  <HeroVideoDialog
                    className="hidden dark:block"
                    animationStyle="from-center"
                    videoSrc="https://www.youtube.com/embed/qh3NGpYRG3I?si=4rb-zSdDkVK9qxxb"
                    thumbnailSrc="https://startup-template-sage.vercel.app/hero-dark.png"
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