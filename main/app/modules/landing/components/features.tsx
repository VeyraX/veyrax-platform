import { Badge } from "@/components/ui/badge";
import Image from "next/image";

export const Features = () => (
  <div className="w-full py-20">
    <div className="container mx-auto px-4">
      <div className="flex flex-col gap-32">
        <div className="flex flex-col items-center text-center mb-10">
          <h1 className="text-5xl md:text-7xl max-w-2xl tracking-tighter font-regular">
            <span className="text-spektr-cyan-50 [word-spacing:-3px] md:[word-spacing:normal]">
              <span className="font-bold">AI Agents</span> is a<br className="md:hidden" /> new way to<br className="md:hidden" /> interact with the web
            </span>
          </h1>
          <p className="text-lg md:text-xl leading-relaxed tracking-tight text-muted-foreground max-w-2xl mt-4">
            Old software, websites and apps will be replaced by AI Agents. Users don't need to manage multiple apps, they just need to get job done.
          </p>
        </div>

        <div className="flex flex-col lg:flex-row gap-20 lg:items-start">
          <div className="flex gap-6 flex-col flex-[1.5] lg:sticky lg:top-20">
            <div className="flex gap-4 flex-col items-start">
              <h2 className="text-3xl md:text-5xl tracking-tighter lg:max-w-xl font-regular text-left">
                Agentic API Format
              </h2>
              <p className="text-xl max-w-xl lg:max-w-sm leading-relaxed tracking-tight text-muted-foreground text-left">
                A seamless API with built-in context management, standardized message format (JSON-RPC 2.0), and tool execution capabilities.
              </p>
            </div>
          </div>
          <div className="relative w-full aspect-[4/3] lg:h-[600px] flex-[2]">
            <Image
              src="/landing/features/feature_1.png"
              alt="Agentic API Format"
              fill
              className="rounded-lg object-contain object-top"
            />
          </div>
        </div>

        <div className="flex flex-col lg:flex-row-reverse gap-20 lg:items-start">
          <div className="flex gap-6 flex-col flex-[1.5] lg:sticky lg:top-20">
            <div className="flex gap-4 flex-col items-start">
              <h2 className="text-3xl md:text-5xl tracking-tighter lg:max-w-xl font-regular text-left">
                Embedded UI Components
              </h2>
              <p className="text-xl max-w-xl lg:max-w-sm leading-relaxed tracking-tight text-muted-foreground text-left">
                Pre-built UI forms for each tool that enhance user interaction with your Agent.
              </p>
            </div>
          </div>
          <div className="relative w-full aspect-[4/3] lg:h-[600px] flex-[2]">
            <Image
              src="/landing/features/feature_2.png"
              alt="Embedded UI Components"
              fill
              className="rounded-lg object-contain object-top"
            />
          </div>
        </div>

        <div className="flex flex-col lg:flex-row gap-20 lg:items-start">
          <div className="flex gap-6 flex-col flex-[1.5] lg:sticky lg:top-20">
            <div className="flex gap-4 flex-col items-start">
              <h2 className="text-3xl md:text-5xl tracking-tighter lg:max-w-xl font-regular text-left">
                Quick Setup
              </h2>
              <p className="text-xl max-w-xl lg:max-w-sm leading-relaxed tracking-tight text-muted-foreground text-left">
                Integrate in just a few clicks with our production-ready components and endpoints.
              </p>
            </div>
          </div>
          <div className="relative w-full aspect-[4/3] lg:h-[600px] flex-[2]">
            <Image
              src="/landing/features/feature_3.png"
              alt="Quick Integration"
              fill
              className="rounded-lg object-contain object-top"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
);
