import { Hero } from "../components/memory/hero";
import { CTA } from "../components/memory/cta"; 
import { Footer } from "../components/footer";

export default function MemoryPageView() {
  return (
    <div className="w-full overflow-x-hidden max-w-none">
      <Hero />
      <CTA />
      <Footer />
    </div>
  );
}