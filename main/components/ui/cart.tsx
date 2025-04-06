'use client';

import type { Variants } from 'motion/react';
import { motion, useAnimation } from 'motion/react';
import type { HTMLAttributes } from 'react';
import { forwardRef, useCallback, useImperativeHandle, useRef } from 'react';
import { cn } from '@/lib/utils';

export interface CartIconHandle {
  startAnimation: () => void;
  stopAnimation: () => void;
}

interface CartIconProps extends HTMLAttributes<HTMLDivElement> {
  size?: number;
}

const cartVariants: Variants = {
  normal: { 
    scale: 1,
    transition: {
      duration: 0.2,
    } 
  },
  animate: {
    scale: [1, 1.1, 1],
    y: [0, -4, 0],
    transition: {
      duration: 0.4,
      times: [0, 0.5, 1],
      ease: 'easeInOut',
    },
  },
};

const pathVariants: Variants = {
  normal: {
    pathLength: 1,
    transition: {
      duration: 0.2,
    }
  },
  animate: {
    pathLength: [1, 0.8, 1],
    transition: {
      duration: 0.4,
      times: [0, 0.5, 1],
      ease: 'easeInOut',
    },
  },
};

const CartIcon = forwardRef<CartIconHandle, CartIconProps>(
  ({ onMouseEnter, onMouseLeave, className, size = 28, ...props }, ref) => {
    const controls = useAnimation();
    const pathControls = useAnimation();
    const isControlledRef = useRef(false);

    useImperativeHandle(ref, () => {
      isControlledRef.current = true;

      return {
        startAnimation: () => {
          controls.start('animate');
          pathControls.start('animate');
        },
        stopAnimation: () => {
          controls.start('normal');
          pathControls.start('normal');
        },
      };
    });

    const handleMouseEnter = useCallback(
      (e: React.MouseEvent<HTMLDivElement>) => {
        if (!isControlledRef.current) {
          controls.start('animate');
          pathControls.start('animate');
        } else {
          onMouseEnter?.(e);
        }
      },
      [controls, pathControls, onMouseEnter]
    );

    const handleMouseLeave = useCallback(
      (e: React.MouseEvent<HTMLDivElement>) => {
        if (!isControlledRef.current) {
          controls.start('normal');
          pathControls.start('normal');
        } else {
          onMouseLeave?.(e);
        }
      },
      [controls, pathControls, onMouseLeave]
    );
    
    return (
      <div
        className={cn(
          `cursor-pointer select-none hover:bg-accent rounded-md transition-colors duration-200 flex items-center justify-center`,
          className
        )}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        {...props}
      >
        <motion.svg
          xmlns="http://www.w3.org/2000/svg"
          width={size}
          height={size}
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          variants={cartVariants}
          animate={controls}
          initial="normal"
          style={{ overflow: 'visible' }}
        >
          <motion.path 
            d="M6.29977 5H21L19 12H7.37671M20 16H8L6 3H3"
            variants={pathVariants}
            animate={pathControls}
            initial="normal"
          />
          <motion.path 
            d="M9 20C9 20.5523 8.55228 21 8 21C7.44772 21 7 20.5523 7 20C7 19.4477 7.44772 19 8 19C8.55228 19 9 19.4477 9 20Z"
            variants={pathVariants}
            animate={pathControls}
            initial="normal"
          />
          <motion.path 
            d="M20 20C20 20.5523 19.5523 21 19 21C18.4477 21 18 20.5523 18 20C18 19.4477 18.4477 19 19 19C19.5523 19 20 19.4477 20 20Z"
            variants={pathVariants}
            animate={pathControls}
            initial="normal"
          />
        </motion.svg>
      </div>
    );
  }
);

CartIcon.displayName = 'CartIcon';

export { CartIcon };
