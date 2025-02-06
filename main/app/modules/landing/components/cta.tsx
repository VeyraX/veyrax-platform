"use client";
import { Button } from "@/components/ui/button";
import Particles from "@/components/ui/particles";
import { useTheme } from "next-themes";
import { useEffect, useState } from "react";
import Link from "next/link";
import { WaitlistDialog } from "../components/waitlist-dialog"
import { MoveRight } from "lucide-react";

export const CTA = () => {
  const { resolvedTheme } = useTheme();
  const [color, setColor] = useState("#ffffff");

  useEffect(() => {
    setColor(resolvedTheme === "dark" ? "#ffffff" : "#000000");
  }, [resolvedTheme]);

  return (
    <div className="w-full">
      <div className="container mx-auto">
        <div className="flex flex-col items-center text-center relative">
          <Particles
            className="absolute inset-0"
            quantity={100}
            ease={80}
            color={color}
            refresh
          />
          <div className="flex flex-col items-center text-center pb-24">
            <div className="flex gap-4 flex-col">
              <h1 className="text-5xl md:text-7xl max-w-2xl tracking-tighter font-regular">
                <span className="text-spektr-cyan-50">AI Agents</span>{" "}
                <span className="font-semibold">will eat the web</span>
              </h1>
              <p className="text-lg md:text-xl leading-relaxed tracking-tight text-muted-foreground max-w-2xl">
                Everything will be consilated and tools development the last bottleneck. We will try our best to help it do so.
              </p>
            </div>
            <div className="flex gap-4 mt-8">
              <WaitlistDialog 
                trigger={
                  <Button size="lg" className="gap-2">
                    Join Waitlist <MoveRight className="h-4 w-4" />
                  </Button>
                }
              />
              <Button variant="outline" size="lg" asChild>
                <Link href="/components">Explore Marketplace</Link>
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
