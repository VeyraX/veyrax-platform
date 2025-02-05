import React from 'react';
import { Toaster } from "@/components/ui/sonner"
import "@/app/globals.css"
import { TopBarMenu } from "@/app/modules/general/components/topbar-menu"

export default async function LandingLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="landing-layout">
        <main>
          <div>
          <TopBarMenu />
            {children}
          </div>
        </main>
      <Toaster />
    </div>
  );
}
