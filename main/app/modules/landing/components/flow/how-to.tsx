"use client";
import { useState, useRef, useEffect } from "react";
import { ChevronDown } from "lucide-react";
import { AnimatePresence, motion } from "framer-motion";
import { featureData } from "./how-to-data";
import Particles from "@/components/ui/particles";
import { useTheme } from "next-themes";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function HowTo() {
  const { resolvedTheme } = useTheme();
  const [color, setColor] = useState("#ffffff");
  const [activeCard, setActiveCard] = useState(1);
  const [progress, setProgress] = useState(0);
  const videoRef = useRef<HTMLVideoElement>(null);
  const currentFeature = featureData.find((f) => f.id === activeCard);

  useEffect(() => {
    setColor(resolvedTheme === "dark" ? "#ffffff" : "#000000");
  }, [resolvedTheme]);

  const handleCardClick = (id: number) => {
    if (id === activeCard) return;
    setProgress(0);
    setActiveCard(id);
  };

  useEffect(() => {
    const duration = currentFeature?.duration || 5000;
    let startTime: number;
    let animationFrame: number;

    const animate = (currentTime: number) => {
      if (!startTime) startTime = currentTime;
      const elapsedTime = currentTime - startTime;
      const progress = Math.min((elapsedTime / duration) * 100, 100);

      setProgress(progress);

      if (progress < 100) {
        animationFrame = requestAnimationFrame(animate);
      } else {
        setActiveCard((prev) => {
          const nextCard = prev + 1;
          return nextCard > featureData.length ? 1 : nextCard;
        });
      }
    };

    animationFrame = requestAnimationFrame(animate);

    return () => {
      if (animationFrame) {
        cancelAnimationFrame(animationFrame);
      }
    };
  }, [activeCard, currentFeature?.duration]);

  return (
    <div className="w-full pb-8 md:pb-16">
      <div className="flex flex-col items-center gap-4 px-4 md:px-8 py-8 md:py-16 relative mb-4 md:mb-8">
        <Particles
          className="absolute inset-0"
          quantity={100}
          ease={80}
          color={color}
          refresh
        />
        <h1 className="text-5xl md:text-7xl tracking-tighter text-center font-regular relative">
          Forget clicking, <span className="text-spektr-cyan-50 font-semibold">just ask</span>
        </h1>
        <p className="text-lg md:text-xl leading-relaxed tracking-tight text-muted-foreground max-w-2xl text-center relative">
          Create, run and automate any workflow with natural language. Our AI Agent will handle the rest.
        </p>
      </div>

      {/* Desktop Layout */}
      <div className="hidden md:flex flex-col items-center w-full space-y-8">
        <div className="w-full px-4 md:px-8 max-w-[1400px] mx-auto">
          <div className="flex flex-row gap-4 w-full">
            {featureData.map((feature) => (
              <div
                key={feature.id}
                className="flex-1 relative"
              >
                {/* Vertical progress bar */}
                <div className="absolute left-0 top-0 w-[2px] h-full bg-gray-200">
                  <motion.div
                    className={`w-full ${
                      activeCard === feature.id 
                        ? 'bg-primary'
                        : 'bg-transparent'
                    }`}
                    initial={{ height: "0%" }}
                    animate={{ 
                      height: activeCard === feature.id ? `${progress}%` : "0%" 
                    }}
                    transition={{ duration: 0.3, ease: "easeOut" }}
                  />
                </div>

                <button
                  onClick={() => handleCardClick(feature.id)}
                  className="w-full text-left focus:outline-none pl-6 py-4 transition-colors"
                >
                  <h3 className="text-lg font-medium mb-2">
                    {feature.title}
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    {feature.description}
                  </p>
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Video section */}
        <div className="relative w-full max-w-7xl">
          <div className="relative w-full border border-border rounded-xl overflow-hidden">
            <video
              ref={videoRef}
              key={currentFeature?.video}
              autoPlay
              muted
              loop
              playsInline
              className="w-full h-auto"
            >
              <source src={currentFeature?.video} type="video/mp4" />
            </video>
          </div>
        </div>
      </div>

      {/* Mobile Layout */}
      <div className="space-y-4 md:hidden px-4 md:px-8">
        {featureData.map((feature) => (
          <Card key={feature.id}>
            <CardHeader>
              <CardTitle className="text-lg font-medium">
                {feature.title}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-black/60 dark:text-gray-500">
                {feature.description}
              </p>
              <div className="relative w-full border border-border rounded-xl overflow-hidden">
                <video
                  autoPlay
                  muted
                  loop
                  playsInline
                  className="w-full h-auto"
                >
                  <source src={feature.video} type="video/mp4" />
                </video>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}