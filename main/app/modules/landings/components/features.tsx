import { Badge } from "@/components/ui/badge";
import Image from "next/image";

export const Features = () => (
  <div className="w-full py-20 lg:py-40">
    <div className="container mx-auto">
      <div className="flex flex-col gap-20">
        <div className="flex flex-col items-center text-center mb-10">
          <h1 className="text-5xl md:text-7xl max-w-2xl tracking-tighter font-regular">
            <span className="text-spektr-cyan-50">AI Agents is a new way to interact with the web</span>
          </h1>
          <p className="text-lg md:text-xl leading-relaxed tracking-tight text-muted-foreground max-w-2xl mt-4">
            Old software, websites and apps will be replaced by AI Agents. Users don't need to manage multiple apps, they just need to get job done.
          </p>
        </div>

        {/* First Block */}
        <div className="flex flex-col lg:flex-row gap-20 lg:items-start">
          <div className="flex gap-4 flex-col flex-1 lg:sticky lg:top-20">
            <div className="flex gap-2 flex-col">
              <h2 className="text-3xl md:text-5xl tracking-tighter lg:max-w-xl font-regular text-left">
                Fetching data from any source
              </h2>
              <p className="text-xl max-w-xl lg:max-w-sm leading-relaxed tracking-tight text-muted-foreground text-left">
                AI Agents connect to any API and database to fetch real-time data from multiple sources simultaneously. This enables automatic data processing from your favorite services without manual input.
              </p>
            </div>
          </div>
          <div className="relative h-[800px] w-full flex-[2] lg:ml-20">
            <Image
              src="/landing/features/feature_1.png"
              alt="Feature 1"
              fill
              className="rounded-md object-contain"
            />
          </div>
        </div>

        {/* Second Block */}
        <div className="flex flex-col lg:flex-row-reverse gap-20 lg:items-start">
          <div className="flex gap-4 flex-col flex-1 lg:sticky lg:top-20">
            <div className="flex gap-2 flex-col">
              <h2 className="text-3xl md:text-5xl tracking-tighter lg:max-w-xl font-regular text-left">
                Uncredieble convenient
              </h2>
              <p className="text-xl max-w-xl lg:max-w-sm leading-relaxed tracking-tight text-muted-foreground text-left">
                Handle all your digital operations from a single interface without switching between different apps. AI Agents automatically process payments, manage subscriptions, and schedule appointments across all connected services.
              </p>
            </div>
          </div>
          <div className="relative h-[800px] w-full flex-[2] lg:mr-20">
            <Image
              src="/landing/features/feature_2.png"
              alt="Feature 2"
              fill
              className="rounded-md object-contain"
            />
          </div>
        </div>

        {/* Third Block */}
        <div className="flex flex-col lg:flex-row gap-20 lg:items-start">
          <div className="flex gap-4 flex-col flex-1 lg:sticky lg:top-20">
            <div className="flex gap-2 flex-col">
              <h2 className="text-3xl md:text-5xl tracking-tighter lg:max-w-xl font-regular text-left">
                Action execution
              </h2>
              <p className="text-xl max-w-xl lg:max-w-sm leading-relaxed tracking-tight text-muted-foreground text-left">
                Execute complex tasks by asking. They automate routine operations that we use to do manually across multiple apps.
              </p>
            </div>
          </div>
          <div className="relative h-[800px] w-full flex-[2] lg:ml-20">
            <Image
              src="/landing/features/feature_3.png"
              alt="Feature 3"
              fill
              className="rounded-md object-contain"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
);
