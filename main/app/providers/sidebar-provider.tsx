'use client';

import React, { ReactNode, useEffect } from 'react';
import { SidebarProvider as UISidebarProvider, useSidebar } from "@/components/ui/sidebar";
import { usePathname } from 'next/navigation';

function SidebarStateController({ children }: { children: ReactNode }) {
  const { setOpen } = useSidebar();
  const pathname = usePathname();
  
  useEffect(() => {
    if (pathname && (
      pathname.startsWith('/flow') || 
      pathname.startsWith('/flows') ||
      pathname.startsWith('/integrations')
    )) {
      setOpen(false);
    }
  }, [pathname, setOpen]);
  
  return <>{children}</>;
}

export function SidebarProvider({ children }: { children: ReactNode }) {
  const defaultOpen = typeof window !== 'undefined' && 
    localStorage.getItem('sidebarState') !== 'closed';
  
  const pathname = usePathname();
  
  const shouldBeCollapsed = pathname && (
    pathname.startsWith('/flow') || 
    pathname.startsWith('/flows') ||
    pathname.startsWith('/integrations')
  );
  const initialOpen = shouldBeCollapsed ? false : defaultOpen;
  
  return (
    <UISidebarProvider defaultOpen={initialOpen}>
      <SidebarStateController>
        {children}
      </SidebarStateController>
    </UISidebarProvider>
  );
}

