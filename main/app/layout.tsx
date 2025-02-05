import type { Metadata } from "next";
import localFont from "next/font/local";
import { SidebarProvider } from "@/components/ui/sidebar";
import { TopBarMenu } from "@/app/modules/general/components/topbar-menu";
import "./globals.css"

const geistSans = localFont({
  src: "./fonts/GeistVF.woff",
  variable: "--font-geist-sans",
  weight: "100 900",
});
const geistMono = localFont({
  src: "./fonts/GeistMonoVF.woff",
  variable: "--font-geist-mono",
  weight: "100 900",
});

export const metadata: Metadata = {
  title: "VeyraX",
  description: "VeyraX AI Agent that can help you with your business",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable}`}
      >
          <main>  
            {children}
          </main>
      </body>
    </html>
  );
}
