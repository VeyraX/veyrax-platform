'use client'
import {
    Lock,
    Globe,
    Layers,
    Rocket
} from "lucide-react";
import { Globe as GlobeComponent } from "@/components/globe";
import { TiltedScroll } from "@/components/ui/tilted-scroll";
import DisplayCards from "@/components/ui/display-cards";
import Particles from "@/components/ui/particles";
import { useTheme } from "next-themes";
import { useEffect, useState } from "react";
  
import { BentoCard, BentoGrid } from "@/components/ui/bento-grid";
import { WaitlistDialog } from "../web/waitlist-dialog";
import Link from "next/link";
import { Button } from "@/components/ui/button";
  
const integrationItems = [
  { id: "slack", text: "Slack", logoSrc: "/logos/slack-logo.svg" },
  { id: "notion", text: "Notion", logoSrc: "/logos/notion-logo.svg" },
  { id: "gmail", text: "Gmail", logoSrc: "/logos/gmail-logo.svg" },
  { id: "jira", text: "Jira", logoSrc: "/logos/jira-logo.svg" },
  { id: "confluence", text: "Confluence", logoSrc: "/logos/confluence-logo.svg" },
  { id: "drive", text: "Google Drive", logoSrc: "/logos/drive-logo.svg" },
  { id: "outlook", text: "Outlook", logoSrc: "/logos/outlook-logo.svg" },
  { id: "perplexity", text: "Perplexity", logoSrc: "/logos/perplexity-logo.svg" },
  { id: "linear", text: "Linear", logoSrc: "/logos/linear-logo.svg" },
  { id: "github", text: "GitHub", logoSrc: "/logos/github-logo.svg" },
  { id: "google-calendar", text: "Google Calendar", logoSrc: "/logos/google-calendar-logo.svg" },
];

const actionCards = [
  {
    icon: <img src="/logos/jira-logo.svg" className="size-4" alt="Jira" />,
    title: "",
    description: "How many open issues on my board?",
    date: "Jira",
    iconClassName: "text-green-500",
    titleClassName: "text-green-500",
    className: "[grid-area:stack] -translate-x-16 -translate-y-10 hover:-translate-y-20 before:absolute before:w-[100%] before:outline-1 before:rounded-xl before:outline-border before:h-[100%] before:content-[''] before:bg-blend-overlay before:bg-background/50 grayscale-[100%] hover:before:opacity-0 before:transition-opacity before:duration:700 hover:grayscale-0 before:left-0 before:top-0 z-0",
  },
  {
    icon: <img src="/logos/gmail-logo.svg" className="size-4" alt="Gmail" />,
    title: "",
    description: "What was the last email I sent?",
    date: "Gmail",
    iconClassName: "text-red-500",
    titleClassName: "text-red-500",
    className: "[grid-area:stack] hover:-translate-y-10 before:absolute before:w-[100%] before:outline-1 before:rounded-xl before:outline-border before:h-[100%] before:content-[''] before:bg-blend-overlay before:bg-background/50 grayscale-[100%] hover:before:opacity-0 before:transition-opacity before:duration:700 hover:grayscale-0 before:left-0 before:top-0 z-10",
  },
  {
    icon: <img src="/logos/google-calendar-logo.svg" className="size-4" alt="Calendar" />,
    title: "",
    description: "What's on my calendar for next week?",
    date: "Google Calendar",
    iconClassName: "text-blue-500",
    titleClassName: "text-blue-500",
    className: "[grid-area:stack] translate-x-16 translate-y-10 hover:-translate-y-1 before:absolute before:w-[100%] before:outline-1 before:rounded-xl before:outline-border before:h-[100%] before:content-[''] before:bg-blend-overlay before:bg-background/50 grayscale-[100%] hover:before:opacity-0 before:transition-opacity before:duration:700 hover:grayscale-0 before:left-0 before:top-0 z-20",
  },
  {
    icon: <img src="/logos/slack-logo.svg" className="size-4" alt="Slack" />,
    title: "",
    description: "What did team discuss about the project?",
    date: "Slack",
    iconClassName: "text-purple-500",
    titleClassName: "text-purple-500",
    className: "[grid-area:stack] translate-x-32 translate-y-20 hover:translate-y-10 z-30",
  },
];

const features = [
    {
      Icon: Globe,
      name: "Connect Everywhere",
      description: "Compatible with any MCP enviroment such as Cursor, VSCode, Windsurf, Claude Desktop, etc.",
      href: "https://docs.veyrax.com/mcp",
      cta: "Check documentation",
      background: (
        <div className="absolute inset-0 overflow-hidden">
          <svg className="h-full w-full opacity-5" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <pattern id="dot-pattern-1" x="0" y="0" width="20" height="20" patternUnits="userSpaceOnUse">
                <circle cx="5" cy="5" r="1" fill="currentColor" />
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#dot-pattern-1)" />
          </svg>
          
          <div className="absolute -top-20 -right-20 w-[120%] h-[120%] opacity-30 pointer-events-none">
            <GlobeComponent className="scale-150 origin-top-right" />
          </div>
        </div>
      ),
      className: "lg:row-start-1 lg:row-end-3 lg:col-start-1 lg:col-end-2 relative overflow-hidden",
      textClassName: "tracking-tight font-normal relative z-10",
    },
    {
      Icon: Lock,
      name: "One Place for Auth",
      description: "Login in all your tools once and use them everywhere.",
      href: "/register",
      cta: "Register",
      useWaitlistDialog: false,
      background: (
        <div className="absolute inset-0 overflow-hidden">
          <svg className="h-full w-full opacity-5" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <pattern id="dot-pattern-2" x="0" y="0" width="20" height="20" patternUnits="userSpaceOnUse">
                <circle cx="5" cy="5" r="1" fill="currentColor" />
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#dot-pattern-2)" />
          </svg>
        </div>
      ),
      className: "lg:row-start-3 lg:row-end-4 lg:col-start-1 lg:col-end-2",
      textClassName: "tracking-tight font-normal",
    },
    {
      Icon: Layers,
      name: "3000+ MCPs and 80+ Integrations",
      description: "with your favorite tools available in one place.",
      href: "https://veyrax.com/marketplace",
      cta: "Visit marketplace",
      background: (
        <div className="absolute inset-0 overflow-hidden">
          <svg className="h-full w-full opacity-5" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <pattern id="dot-pattern-3" x="0" y="0" width="20" height="20" patternUnits="userSpaceOnUse">
                <circle cx="5" cy="5" r="1" fill="currentColor" />
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#dot-pattern-3)" />
          </svg>
          
          <div className="absolute right-0 top-0 bottom-0 w-1/2 flex items-center justify-center z-10">
            <TiltedScroll 
              items={integrationItems}
              className="w-full h-full"
            />
          </div>
        </div>
      ),
      className: "lg:col-start-2 lg:col-end-4 lg:row-start-1 lg:row-end-2 relative",
      textClassName: "tracking-tight font-normal relative z-20 max-w-[45%]",
    },
    {
      Icon: Rocket,
      name: "1500+ Actions",
      description:
        "that AI Agent can execute.",
      href: "https://veyrax.com/marketplace",
      cta: "Visit marketplace",
      background: (
        <div className="absolute inset-0 overflow-hidden">
          <svg className="h-full w-full opacity-5" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <pattern id="dot-pattern-4" x="0" y="0" width="20" height="20" patternUnits="userSpaceOnUse">
                <circle cx="5" cy="5" r="1" fill="currentColor" />
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#dot-pattern-4)" />
          </svg>
          
          <div className="absolute top-0 right-0 w-[70%] h-full flex items-center justify-end z-10">
            <div className="scale-110 origin-center transform-gpu">
              <DisplayCards cards={actionCards} />
            </div>
          </div>
        </div>
      ),
      className: "lg:col-start-2 lg:col-end-4 lg:row-start-2 lg:row-end-4",
      textClassName: "tracking-tight font-normal relative z-20 max-w-[30%]",
    },
];
  
export function Features() {
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
      
      <div className="text-center mb-12 relative z-10">
        <h2 className="text-5xl md:text-7xl max-w-2xl tracking-tighter font-regular mx-auto">
          <div>
            <span className="text-spektr-cyan-50">Powerful features</span>
          </div>
          <div>
            <span className="font-semibold">for your workflow</span>
          </div>
        </h2>
        <p className="text-lg md:text-xl leading-relaxed tracking-tight text-muted-foreground max-w-2xl text-center mx-auto mt-4">
          Seamlessly connect your tools with AI, so you can focus on what matters.
        </p>
      </div>

      <div className="flex justify-center w-full">
        <BentoGrid className="px-4 md:px-8 py-6 lg:grid-rows-3 lg:grid-cols-3 max-w-[1400px] w-full">
          {features.map((feature) => (
            <BentoCard key={feature.name} {...feature} />
          ))}
        </BentoGrid>
      </div>
    </div>
  );
}
  