'use client';

import React, { useState, useEffect } from 'react';
import { Plus, Menu, MoreHorizontal, Link, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { SidebarToggle } from './toggle-sidebar';
import { useRouter } from 'next/navigation';
import { useSidebar } from '@/components/ui/sidebar';
import { AccountSettingsDialog } from '@/app/modules/settings/pages/settings-page';
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { getUserProfile } from '@/app/modules/settings/api/api.settings';
import { UserProfile } from '@/app/modules/settings/api/types.settings';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Settings, CreditCard, Moon, Sun, Laptop, LogOut } from 'lucide-react';
import { UserDropdown } from './profile-dropdown';

export function Header({ 
  className, 
  isShowChat=true, 
  chatName="" 
}: { 
  className?: string, 
  isShowChat?: boolean,
  chatName?: string 
}) {
  const router = useRouter();
  const [showCheck, setShowCheck] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [theme, setTheme] = useState<'light' | 'dark' | 'system'>('system');

  useEffect(() => {
    async function loadProfile() {
      const data = await getUserProfile()
      setProfile(data)
    }
    loadProfile()
  }, [])

  const handleCopyLink = () => {
    navigator.clipboard.writeText(window.location.href);
    setShowCheck(true);
    setTimeout(() => setShowCheck(false), 2000); 
  }
  
  return (
    <>
      <header className={`flex items-center bg-background justify-between gap-2 px-4 py-2 ${className || ''}`}>
        <div className="flex items-center gap-2">
          <SidebarToggle className="hidden md:flex" />
          {isShowChat && (
            <Button
              variant="ghost"
              size="icon"
              onClick={() => router.push('/agent/new')}
            >
              <Plus className="h-5 w-5" />
              <span className="sr-only">New Chat</span>
            </Button>
          )}
        </div>
        
        {isShowChat && chatName && (
          <nav className="flex items-center text-sm flex-1 justify-center">
            <span className="tracking-tighter text-foreground">
              {chatName}
            </span>
          </nav>
        )}
        
        <div className="flex items-center gap-2">
          {isShowChat && (
            <>
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
                <span className="sr-only">More options</span>
              </Button>
              <div className="h-6 w-[1px] bg-border" />
            </>
          )}
          <UserDropdown 
            profile={profile}
            onOpenSettings={() => setShowSettings(true)}
          />
        </div>
      </header>

      <AccountSettingsDialog 
        open={showSettings} 
        onOpenChange={setShowSettings}
      />
    </>
  );
}
