"use client";

import { Button } from "@/components/ui/button";
import Particles from "@/components/ui/particles";
import { useTheme } from "next-themes";
import { useEffect, useState } from "react";
import Link from "next/link";
import { MoveRight, Code2, Terminal, PlayCircle, ServerIcon, Cpu, Database, Brain } from "lucide-react";

export const CTA = () => {
  const { resolvedTheme } = useTheme();
  const [color, setColor] = useState("#ffffff");

  useEffect(() => {
    setColor(resolvedTheme === "dark" ? "#ffffff" : "#000000");
  }, [resolvedTheme]);

  return (
    <div className="flex flex-col items-center w-full relative py-8 md:py-16 mb-8 md:mb-16">
      <Particles
        className="absolute inset-0"
        quantity={100}
        ease={80}
        color={color}
        refresh
      />
      
      <div className="text-center mb-12 relative z-10 px-4 md:px-8">
        <h2 className="text-5xl md:text-7xl max-w-3xl tracking-tighter font-regular">
          <span className="text-spektr-cyan-50">Enable Memory </span>
          <span className="font-semibold">everywhere</span>
        </h2>
        <p className="text-lg md:text-xl leading-relaxed tracking-tight text-muted-foreground max-w-2xl text-center mx-auto mt-4">
          VeyraX Memory is already available for you. Just sign up, connect it, and start making your Agents truly personal.
        </p>
      </div>

      <div className="flex flex-col md:flex-row gap-8 max-w-5xl w-full px-4 relative z-10">
        <Link href="https://docs.veyrax.com/mcp/introduction" target="_blank" rel="noopener noreferrer" className="flex-1 rounded-xl border border-border p-6 bg-background/50 backdrop-blur hover:bg-background/70 transition-all group">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 rounded-lg bg-white">
              <Brain className="w-6 h-6 text-black" />
            </div>
            <h3 className="text-2xl font-medium">MCP</h3>
            <MoveRight className="w-4 h-4 ml-1 transform transition-transform group-hover:translate-x-1" />
          </div>
          <p className="text-muted-foreground">
            Access VeyraX tools and memory through Model Context Protocol (MCP).
          </p>
        </Link>

        <Link href="https://docs.veyrax.com/api-reference/introduction" target="_blank" rel="noopener noreferrer" className="flex-1 rounded-xl border border-border p-6 bg-background/50 backdrop-blur hover:bg-background/70 transition-all group">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 rounded-lg bg-white">
              <ServerIcon className="w-6 h-6 text-black" />
            </div>
            <h3 className="text-2xl font-medium">API</h3>
            <MoveRight className="w-4 h-4 ml-1 transform transition-transform group-hover:translate-x-1" />
          </div>
          <p className="text-muted-foreground">
            Integrate VeyraX tools and memory directly into your applications with our API.
          </p>
        </Link>

        <Link href="/agent/new" className="flex-1 rounded-xl border border-border p-6 bg-background/50 backdrop-blur hover:bg-background/70 transition-all group">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 rounded-lg bg-white">
              <PlayCircle className="w-6 h-6 text-black" />
            </div>
            <h3 className="text-2xl font-medium">Playground</h3>
            <MoveRight className="w-4 h-4 ml-1 transform transition-transform group-hover:translate-x-1" />
          </div>
          <p className="text-muted-foreground">
            Test and experiment with VeyraX tools in our playground environment.
          </p>
        </Link>
      </div>
    </div>
  );
};