import React from 'react';
import { Toaster } from "@/components/ui/sonner"
import { SidebarProvider } from "@/components/ui/sidebar"
import "@/app/globals.css"
import { TopBarMenu } from "@/app/modules/general/components/topbar-menu"

export default async function EndpointsLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="components-layout">
      <SidebarProvider defaultOpen={true}>
        <main className="flex-1 flex flex-col h-screen">
          <div className="flex-1">
          <TopBarMenu />
            {children}
          </div>
        </main>
      </SidebarProvider>
      <Toaster />
    </div>
  );
}
