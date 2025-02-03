'use client';

import React, { useState } from 'react';
import { Plus, Menu, MoreHorizontal, Link, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { SidebarToggle } from './toggle-sidebar';
import { useRouter } from 'next/navigation';
import { useSidebar } from '@/components/ui/sidebar';

export function Header({ className }: { className?: string }) {
  const router = useRouter();
  const [showCheck, setShowCheck] = useState(false);

  const handleCopyLink = () => {
    navigator.clipboard.writeText('https://veyrax.com/agent/');
    setShowCheck(true);
    setTimeout(() => setShowCheck(false), 2000); 
  }
  
  return (
    <header className={`flex items-center bg-background justify-between gap-2 px-4 py-2 ${className || ''}`}>
      <div className="flex items-center gap-2">
        <SidebarToggle className="hidden md:flex" />
        <Button
          variant="ghost"
          size="icon"
          onClick={() => window.location.reload()}
        >
          <Plus className="h-5 w-5" />
          <span className="sr-only">New Chat</span>
        </Button>
      </div>
      <div className="flex items-center gap-2">
        <Button variant="ghost" size="icon" onClick={handleCopyLink}>
          {showCheck ? (
            <Check className="h-5 w-5" />
          ) : (
            <Link className="h-5 w-5" />
          )}
          <span className="sr-only">Share</span>
        </Button>
        <Button variant="ghost" size="icon">
          <MoreHorizontal className="h-5 w-5" />
          <span className="sr-only">Settings</span>
        </Button>
      </div>
    </header>
  );
}
