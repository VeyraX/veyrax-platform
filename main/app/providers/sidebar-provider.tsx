'use client';

import React, { ReactNode } from 'react';
import { SidebarProvider as UISidebarProvider } from "@/components/ui/sidebar";

export function SidebarProvider({ children }: { children: ReactNode }) {
  const defaultOpen = typeof window !== 'undefined' && 
    localStorage.getItem('sidebarState') !== 'closed';
  
  return (
    <UISidebarProvider defaultOpen={defaultOpen}>
      {children}
    </UISidebarProvider>
  );
}

