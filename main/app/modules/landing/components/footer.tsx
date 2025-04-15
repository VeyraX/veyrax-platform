"use client";

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Facebook, Instagram, Linkedin, Twitter } from "lucide-react"
import Image from "next/image"
import X from '@/public/logos/x-logo.svg';
import LinkedIn from '@/public/logos/linkedin-logo.svg';

export const Footer = () => {
  const scrollToSection = (elementId: string) => {
    const element = document.getElementById(elementId);
    element?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <footer className="bg-primary dark:bg-primary/90 py-12 text-white">
      <div className="container mx-auto px-4 md:px-6">
        <div className="flex flex-col items-center">
          <div className="mb-8 rounded-full h-10 w-10">
            <img src="/logo_light.svg" alt="Logo" className="h-10 w-10" />
          </div>
          <nav className="mb-8 flex flex-wrap justify-center gap-6">
            <a href="/" className="transition-colors hover:text-gray-300 dark:hover:text-gray-200">Home</a>
            <a 
              href="/mcp" 
              className="transition-colors hover:text-gray-300 dark:hover:text-gray-200"
            >
              MCP
            </a>
            <a href="/marketplace" className="transition-colors hover:text-gray-300 dark:hover:text-gray-200">Integrations</a>
            <a href="/web/flow" className="transition-colors hover:text-gray-300 dark:hover:text-gray-200">Flow</a>
          </nav>
          <div className="mb-8 flex space-x-4">
            <Button
              variant="outline"
              size="icon"
              className="rounded-full border-white/60 dark:border-white/50 hover:bg-white/10 dark:hover:bg-white/20"
              asChild
            >
              <a
                href="https://x.com/veyraxai"
                target="_blank"
                rel="noopener noreferrer"
              >
                <Image src={X} alt="X" className="h-4 w-4" />
              </a>
            </Button>
            <Button
              variant="outline"
              size="icon"
              className="rounded-full border-white/60 dark:border-white/50 hover:bg-white/10 dark:hover:bg-white/20"
              asChild
            >
            </Button>
          </div>
          <div className="text-center">
            <div className="flex justify-center gap-4 mb-2">
              <a href="/terms" className="text-sm text-white/80 hover:text-white dark:text-white/70 dark:hover:text-white">Terms of Service</a>
              <a href="/privacy" className="text-sm text-white/80 hover:text-white dark:text-white/70 dark:hover:text-white">Privacy Policy</a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  )
}