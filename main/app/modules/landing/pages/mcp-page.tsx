"use client";

import { Hero } from "../components/mcp/hero";
import { Features } from "../components/mcp/features";
import { Idea } from "../components/mcp/idea";
import HowTo from "../components/mcp/how-to";
import { Footer } from "../components/footer";
import { CTA } from "../components/mcp/cta";

export default function MCPPage() {
  return (
    <>
      <Hero />
      <Idea />
      <HowTo />
      <Features />
      <CTA />
      <Footer />
    </>
  );
}