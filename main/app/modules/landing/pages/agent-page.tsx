'use client'
import { Hero } from "../components/agent/hero"
import { useEffect } from "react"
import { Footer } from "../components/footer"

export default function AgentPageWeb() {
  useEffect(() => {
    const hash = window.location.hash;
    if (hash === '#text-block') {
      document.getElementById('text-block')?.scrollIntoView({ behavior: 'smooth' });
    }
  }, []);

  return (
    <div className="flex flex-col gap-32">
      <Hero />
      <Footer />
    </div>
  )
}