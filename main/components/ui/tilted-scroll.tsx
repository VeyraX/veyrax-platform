'use client'
import { cn } from "@/lib/utils"
import { motion, useAnimationControls } from 'framer-motion';
import { useEffect } from 'react';

interface TiltedScrollItem {
  id: string;
  text: string;
  logoSrc?: string;
}

interface TiltedScrollProps {
  items?: TiltedScrollItem[];
  className?: string;
}

export function TiltedScroll({ 
  items = defaultItems,
  className 
}: TiltedScrollProps) {
  const controls = useAnimationControls();
  
  useEffect(() => {
    controls.start({
      y: [0, -1000],
      transition: {
        y: {
          repeat: Infinity,
          repeatType: "loop",
          duration: 30,
          ease: "linear"
        }
      }
    });
    
    return () => {
      controls.stop();
    };
  }, [controls]);

  const scrollItems = [...items, ...items, ...items, ...items];
  
  return (
    <div className={cn("flex items-center justify-center", className)}>
      <div className="relative overflow-hidden [mask-composite:intersect] [mask-image:linear-gradient(to_right,transparent,black_5rem),linear-gradient(to_left,transparent,black_5rem),linear-gradient(to_bottom,transparent,black_5rem),linear-gradient(to_top,transparent,black_5rem)]">
        <motion.div 
          animate={controls}
          style={{ 
            transformOrigin: "center center",
            transform: "skewX(-10deg)"
          }}
          className="flex flex-col gap-5 w-[300px]"
        >
          {scrollItems.map((item, index) => (
            <div
              key={`${item.id}-${index}`}
              className="group flex items-center gap-2 cursor-pointer rounded-md border border-border/40 bg-gradient-to-b from-background/80 to-muted/80 p-4 shadow-md transition-all duration-300 ease-in-out hover:scale-105 hover:-translate-x-1 hover:-translate-y-1 hover:shadow-xl dark:border-border"
            >
              {item.logoSrc ? (
                <img src={item.logoSrc} alt={item.text} className="h-6 w-6 mr-2" />
              ) : (
                <CheckCircleIcon className="h-6 w-6 mr-2 stroke-foreground/40 transition-colors group-hover:stroke-foreground" />
              )}
              <p className="text-foreground/80 transition-colors group-hover:text-foreground">
                {item.text}
              </p>
            </div>
          ))}
        </motion.div>
      </div>
    </div>
  )
}

function CheckCircleIcon(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      strokeWidth="1"
      strokeLinecap="round"
      strokeLinejoin="round"
      {...props}
    >
      <path d="M3.85 8.62a4 4 0 0 1 4.78-4.77 4 4 0 0 1 6.74 0 4 4 0 0 1 4.78 4.78 4 4 0 0 1 0 6.74 4 4 0 0 1-4.77 4.78 4 4 0 0 1-6.75 0 4 4 0 0 1-4.78-4.77 4 4 0 0 1 0-6.76Z" />
      <path d="m9 12 2 2 4-4" />
    </svg>
  )
}

const defaultItems: TiltedScrollItem[] = [
  { id: "1", text: "Item 1" },
  { id: "2", text: "Item 2" },
  { id: "3", text: "Item 3" },
  { id: "4", text: "Item 4" },
  { id: "5", text: "Item 5" },
  { id: "6", text: "Item 6" },
  { id: "7", text: "Item 7" },
  { id: "8", text: "Item 8" },
]