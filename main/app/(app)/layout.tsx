import React from 'react';
import { Toaster } from "@/components/ui/sonner"
import { SidebarInset } from "@/components/ui/sidebar"
import { AppSidebar } from "@/app/modules/general/components/app-sidebar"
import { ThemeProvider } from "@/app/providers/theme-provider"
import { ReactQueryProvider } from "@/app/providers/react-query-provider"
import { SidebarProvider } from "@/app/providers/sidebar-provider"
import "@/app/globals.css"

export default function AppLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <ThemeProvider
      attribute="class"
      defaultTheme="light"
      enableSystem
      disableTransitionOnChange
    >
      <ReactQueryProvider>
        <div className="app-layout bg-light-special-background min-h-screen flex">
          <SidebarProvider>
            <AppSidebar collapsible="icon" />
            <main className="flex-1 flex flex-col overflow-hidden">
              <SidebarInset>
                <div className="flex-1 flex flex-col">
                  {children}
                </div>
              </SidebarInset>
            </main>
          </SidebarProvider>
          <Toaster />
        </div>
      </ReactQueryProvider>
    </ThemeProvider>
  );
}
