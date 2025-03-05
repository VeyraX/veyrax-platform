"use client";

import { useEffect, useState } from "react";
import { useTheme } from "next-themes";
import Particles from "@/components/ui/particles";
import { Terminal, Code2 } from "lucide-react";

export function Idea() {
  const { resolvedTheme } = useTheme();
  const [color, setColor] = useState("#ffffff");

  useEffect(() => {
    setColor(resolvedTheme === "dark" ? "#ffffff" : "#000000");
  }, [resolvedTheme]);

  return (
    <div className="flex flex-col items-center w-full relative py-8 md:py-16">
      <Particles
        className="absolute inset-0"
        quantity={100}
        ease={80}
        color={color}
        refresh
      />
      
      <div className="text-center mb-12 relative z-10 px-4 md:px-8">
        <h2 className="text-5xl md:text-7xl max-w-3xl tracking-tighter font-regular mx-auto">
          <div>
            <span className="text-spektr-cyan-50">Our Core Architecture</span>
          </div>
          <div>
            <span className="font-semibold">just one tool</span>
          </div>
        </h2>
        <p className="text-lg md:text-xl leading-relaxed tracking-tight text-muted-foreground max-w-2xl text-center mx-auto mt-4">
          While others require you to connect dozens of services with separate credentials in MCP, 
          we handle everything through a single tool with just two methods that can route to any tool.
        </p>
      </div>

      <div className="flex flex-col md:flex-row gap-8 max-w-4xl w-full px-4 relative z-10">
        <div className="flex-1 rounded-xl border border-border p-6 bg-background/50 backdrop-blur">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 rounded-lg bg-white">
              <Terminal className="w-6 h-6 text-black" />
            </div>
            <h3 className="text-2xl font-medium">get_tools</h3>
          </div>
          <p className="text-muted-foreground">
            One method to discover all available tools. All tools are already connected through us — no need to set up dozens of integrations.
          </p>
        </div>

        <div className="flex-1 rounded-xl border border-border p-6 bg-background/50 backdrop-blur">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 rounded-lg bg-white">
              <Code2 className="w-6 h-6 text-black" />
            </div>
            <h3 className="text-2xl font-medium">tool_call</h3>
          </div>
          <p className="text-muted-foreground">
            Execute any action by specifying just the tool, method, and parameters. We handle routing, authentication, and connections internally.
          </p>
        </div>
      </div>
    </div>
  );
}
