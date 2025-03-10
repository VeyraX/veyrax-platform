"use client";

import { useEffect, useState } from "react";
import { MoveRight, ArrowLeft, ArrowRight, Play } from "lucide-react";
import { Button } from "@/components/ui/button";
import Particles from "@/components/ui/particles";
import { useTheme } from "next-themes";
import { BorderBeam } from "@/components/ui/border-beam";
import HeroVideoDialog from "@/components/ui/hero-video-dialog";
import { Input } from "@/components/ui/input";
import { WaitlistService } from '../../api/api.service';
import { Alert, AlertDescription } from "@/components/ui/alert";
import { validateEmail } from '@/lib/utils/email-validator';
import { WaitlistDialog } from "../web/waitlist-dialog";
import Link from "next/link";
import {
  Carousel,
  CarouselApi,
  CarouselContent,
  CarouselItem,
} from "@/components/ui/carousel";
import { heroData } from "./hero-data";
import VideoDialog from "./video-dialog";

export const Hero = () => {
  const { resolvedTheme } = useTheme();
  const [color, setColor] = useState("#ffffff");
  const [email, setEmail] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);
  const [showForm, setShowForm] = useState(true);
  const [carouselApi, setCarouselApi] = useState<CarouselApi>();
  const [currentSlide, setCurrentSlide] = useState(0);

  useEffect(() => {
    setColor(resolvedTheme === "dark" ? "#ffffff" : "#000000");
  }, [resolvedTheme]);

  useEffect(() => {
    if (message?.type === 'error') {
      const timer = setTimeout(() => {
        setMessage(null);
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [message]);

  useEffect(() => {
    if (!carouselApi) {
      return;
    }
    const updateSelection = () => {
      setCurrentSlide(carouselApi.selectedScrollSnap());
    };
    updateSelection();
    carouselApi.on("select", updateSelection);
    return () => {
      carouselApi.off("select", updateSelection);
    };
  }, [carouselApi]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setMessage(null);

    if (!validateEmail(email)) {
      setMessage({
        type: 'error',
        text: 'Please enter a valid email address'
      });
      setIsLoading(false);
      return;
    }

    const result = await WaitlistService.addToWaitlist(email);
    
    setMessage({
      type: result.data ? 'success' : 'error',
      text: result.data 
        ? "You've been added to the waitlist. We'll be in touch soon!"
        : result.error.message.includes('unique constraint') 
          ? "This email is already on the waitlist. We'll be in touch soon!"
          : result.error.message
    });

    if (result.data) {
      setEmail('');
      setShowForm(false);
    }
    
    setIsLoading(false);
  };

  return (
    <div className="w-full pt-8">
      <div className="w-full h-full flex items-center justify-center px-4 md:px-8">
        <div className="flex items-center justify-center py-8 md:py-16">
          <div className="container mx-auto">
            <div className="flex gap-4 items-center justify-center flex-col relative">
              <Particles
                className="absolute inset-0"
                quantity={100}
                ease={80}
                color={color}
                refresh
              />
              
              <div className="flex gap-4 flex-col items-center">
                <div className="flex flex-col items-center gap-3">
                  <span className="text-spektr-cyan-50 text-sm md:text-base px-4 py-1.5 rounded-full bg-spektr-cyan-50/10 border border-spektr-cyan-50/20 flex items-center gap-1.5 transition-colors hover:bg-black hover:text-white hover:border-black cursor-pointer">
                    VeyraX Memory
                  </span>
                  <h1 className="text-5xl md:text-7xl max-w-2xl tracking-tighter text-center font-regular">
                    <div>
                      <div><span className="font-semibold">Equip your favorite</span> </div>
                      <div>agents with superpower</div>
                    </div>
                  </h1>
                </div>

                <p className="text-lg md:text-xl leading-relaxed tracking-tight text-muted-foreground max-w-2xl text-center">
                  VeyraX Memory is a tool that allows Agents remember about you and your tools. All the time, in all environments where you use VeyraX.{" "}
                </p>
              </div>

              <div className="flex flex-row items-center gap-4 w-full max-w-md justify-center">
                <Link href="/register">
                  <Button className="gap-2">
                    Get Access <MoveRight className="w-4 h-4" />
                  </Button>
                </Link>
                
                <Link href="https://docs.veyrax.com/memory" target="_blank" rel="noopener noreferrer">
                  <Button variant="outline">
                    Explore Docs
                  </Button>
                </Link>
              </div>

              <div className="relative mx-auto w-[100vw] -translate-x-1/2 left-1/2 z-10 overflow-hidden mt-4 md:mt-0">
                <Carousel
                  setApi={setCarouselApi}
                  opts={{
                    align: "start",
                    breakpoints: {
                      "(max-width: 768px)": {
                        dragFree: true,
                      },
                    },
                  }}
                  className="w-full"
                >
                  <div className="flex items-center justify-end mb-4 px-4 md:px-8 lg:px-12">
                    <div className="flex gap-2">
                      <Button
                        size="icon"
                        variant="outline"
                        onClick={() => carouselApi?.scrollPrev()}
                        disabled={currentSlide === 0}
                        className="rounded-full"
                      >
                        <ArrowLeft className="h-4 w-4" />
                        <span className="sr-only">Previous slide</span>
                      </Button>
                      <Button
                        size="icon"
                        variant="outline"
                        onClick={() => carouselApi?.scrollNext()}
                        disabled={currentSlide === heroData.items.length - 1}
                        className="rounded-full"
                      >
                        <ArrowRight className="h-4 w-4" />
                        <span className="sr-only">Next slide</span>
                      </Button>
                    </div>
                  </div>
                  
                  <CarouselContent className="ml-[calc(40vw-180px)] md:ml-[calc(40vw-200px)] lg:ml-[calc(35vw-220px)]">
                    {heroData.items.map((item) => (
                      <CarouselItem
                        key={item.id}
                        className="max-w-[360px] pl-[20px] lg:max-w-[440px]"
                      >
                        <div className="group rounded-xl">
                          <div className="group relative h-full min-h-[27rem] max-w-full overflow-hidden rounded-xl md:aspect-[16/9] lg:aspect-[16/9]">
                            <video
                              src={item.video}
                              autoPlay
                              loop
                              muted
                              playsInline
                              className="absolute h-full w-full object-cover object-center transition-transform duration-300 group-hover:scale-105"
                            />
                            <div className="absolute inset-0 h-full bg-[linear-gradient(hsl(var(--primary)/0),hsl(var(--primary)/0.4),hsl(var(--primary)/0.8)_100%)] mix-blend-multiply" />
                            <div className="absolute inset-x-0 bottom-0 flex flex-col items-start p-6 text-primary-foreground md:p-8">
                              <div className="mb-4 text-xl font-semibold">
                                {item.summary}
                              </div>
                              <p className="mb-6 text-sm text-primary-foreground/80">
                                {item.description}
                              </p>
                              <VideoDialog videoSrc={item.video}>
                                <Button 
                                  variant="link" 
                                  className="text-primary-foreground"
                                >
                                  <Play className="h-4 w-4" /> Watch Video
                                </Button>
                              </VideoDialog>
                            </div>
                          </div>
                        </div>
                      </CarouselItem>
                    ))}
                  </CarouselContent>
                </Carousel>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};