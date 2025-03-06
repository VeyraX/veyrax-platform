import React from 'react';
import Link from 'next/link';

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="auth-layout flex flex-col min-h-screen">
      <main className="flex-grow flex items-center justify-center">
        {children}
      </main>
      <footer className="w-full py-2 bg-white border-t">
        <div className="container mx-auto px-4">
          <div className="flex justify-center items-center">
            <Link href="/terms" className="text-xs text-gray-600 hover:text-blue-600 hover:underline">
              Terms of Service
            </Link>
            <span className="mx-2 text-gray-400">|</span>
            <Link href="/privacy" className="text-xs text-gray-600 hover:text-blue-600 hover:underline">
              Privacy Policy
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
}