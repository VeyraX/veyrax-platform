"use client";
import { useTheme } from "next-themes";
import { featureData } from "./how-to.data";
import { cn } from "@/lib/utils";
import Link from "next/link";
import { ArrowRight } from "lucide-react";
import Particles from "@/components/ui/particles";

export default function HowTo() {
  const { resolvedTheme } = useTheme();
  const color = resolvedTheme === "dark" ? "#ffffff" : "#000000";

  return (
    <section className="w-full py-16 md:py-32">
      <div className="flex flex-col items-center w-full relative mb-16">
        <Particles
          className="absolute inset-0"
          quantity={100}
          ease={80}
          color={color}
          refresh
        />
        <div className="text-center relative z-10">
          <h2 className="text-5xl md:text-7xl tracking-tighter font-regular mx-auto">
            <div>
              <span className="text-spektr-cyan-50">Get any tool you want</span>
            </div>
            <div>
              <span className="font-semibold">with VeyraX MCP</span>
            </div>
          </h2>
          <p className="text-lg md:text-xl leading-relaxed tracking-tight text-muted-foreground max-w-2xl text-center mx-auto mt-4">
            VeyraX cover all MCP steps: deployment, connection, and usage. You do not need to manage any infrastructure or authentication, just connect your tools and use them.
          </p>
        </div>
      </div>

      <div className="space-y-32">
        {featureData.map((feature, index) => (
          <div key={feature.id} className="container mx-auto px-4 md:px-8">
            <div 
              className={cn(
                "flex flex-col lg:flex-row items-center gap-16 lg:gap-24",
                index % 2 !== 0 && "lg:flex-row-reverse"
              )}
            >
              <div className="w-full lg:w-1/3 shrink-0">
                <div className="flex flex-col gap-5 text-left">
                  <h3 className="text-3xl tracking-tighter font-semibold">
                    {feature.title}
                  </h3>
                  <p className="text-lg leading-relaxed tracking-tight text-muted-foreground">
                    {feature.longDescription}
                  </p>
                  
                  <div className="pt-2">
                    <Link 
                      href={feature.ctaLink} 
                      className="group inline-flex items-center text-spektr-cyan-50 hover:text-spektr-cyan-100 transition-colors"
                    >
                      <span className="group-hover:underline">{feature.ctaText}</span> 
                      <ArrowRight className="ml-2 h-4 w-4 transition-transform duration-300 group-hover:translate-x-1" />
                    </Link>
                  </div>
                </div>
              </div>
              
              <div className="w-full lg:w-2/3">
                <div className="relative w-full overflow-hidden rounded-xl">
                  <video
                    key={feature.video}
                    autoPlay
                    muted
                    loop
                    playsInline
                    className="w-full aspect-video object-cover"
                  >
                    <source src={feature.video} type="video/mp4" />
                    Your browser does not support the video tag.
                  </video>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}