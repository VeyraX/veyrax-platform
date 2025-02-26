'use client'
import { Features } from "../components/features"
import { Hero } from "../components/web/hero"
import { CTA } from "../components/web/cta"
import { TextBlock } from "../components/text"
import { useEffect } from "react"
import { Footer } from "../components/footer"
export default function LandingPage() {
  useEffect(() => {
    const hash = window.location.hash;
    if (hash === '#text-block') {
      document.getElementById('text-block')?.scrollIntoView({ behavior: 'smooth' });
    }
  }, []);

  return (
    <div className="flex flex-col gap-32">
      <Hero />
      <TextBlock />
      <Features />
      <CTA />
      <Footer />
    </div>
  )
}