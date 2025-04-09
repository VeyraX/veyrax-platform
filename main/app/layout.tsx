import type { Metadata } from "next";
import localFont from "next/font/local";
import { SidebarProvider } from "@/components/ui/sidebar";
import { TopBarMenu } from "@/app/modules/general/components/topbar-menu";
import "./globals.css"
import { PostHogProvider } from "@/app/providers/posthog";

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
  description: "VeyraX is Agentic Component Interface",
  openGraph: {
    title: "VeyraX",
    description: "VeyraX is Agentic Component Interface",
    type: "website",
    url: "https://veyrax.com",
    images: [
      {
        url: "/landing/social_cover.png",
        width: 1200,
        height: 630,
        alt: "VeyraX",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "VeyraX",
    description: "VeyraX is Agentic Component Interface",
    images: ["/landing/social_cover.png"],
  },
  verification: {
    google: "M87s6BmvzBfZcTPzKC_IdrsZKCoMINTWwASkeDmDySM",
  },
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
        <PostHogProvider>
          <main>  
            {children}
          </main>
        </PostHogProvider>
      </body>
    </html>
  );
}
