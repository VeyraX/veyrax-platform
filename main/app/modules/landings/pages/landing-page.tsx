'use client'
import { Features } from "../components/features"
import { Hero } from "../components/hero"
import { Components } from "../components/components"
import { TextBlock } from "../components/text"
import { useEffect } from "react"

export default function LandingPage() {
  useEffect(() => {
    const hash = window.location.hash;
    if (hash === '#text-block') {
      document.getElementById('text-block')?.scrollIntoView({ behavior: 'smooth' });
    }
  }, []);

  return (
    <>
      <Hero />
      <TextBlock />
      <Features />
      <Components />
    </>
  )
}