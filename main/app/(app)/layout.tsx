import React from 'react';
import { Toaster } from "@/components/ui/sonner"
import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar"
import { AppSidebar } from "@/app/modules/general/components/app-sidebar"
import { ThemeProvider } from "@/app/providers/theme-provider"
import "@/app/globals.css"

export default async function AppLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <ThemeProvider
      attribute="class"
      defaultTheme="system"
      enableSystem
      disableTransitionOnChange
    >
      <div className="app-layout bg-light-special-background">
        <SidebarProvider defaultOpen={true}>
          <AppSidebar collapsible="offcanvas" />
          <main className="flex-1 flex flex-col h-screen">
            <div className="flex-1">
              <SidebarInset>{children}</SidebarInset>
            </div>
          </main>
        </SidebarProvider>
        <Toaster />
      </div>
    </ThemeProvider>
  );
}
