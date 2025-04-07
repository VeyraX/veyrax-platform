'use client';

import React, { useState, useEffect } from 'react';
import { Plus, Menu, MoreHorizontal, Link, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { SidebarToggle } from './toggle-sidebar';
import { useRouter } from 'next/navigation';
import { useSidebar } from '@/components/ui/sidebar';
import { AccountSettingsDialog } from '@/app/modules/settings/pages/settings-page';
import { getUserProfile, isUserOnFreePlan } from '@/app/modules/settings/api/api.settings';
import { UserDropdown } from './profile-dropdown';
import { UserProfile } from '@/app/modules/settings/api/types.settings';

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
  const [settingsTab, setSettingsTab] = useState<'account' | 'api-key' | 'billing'>('account');
  const [theme, setTheme] = useState<'light' | 'dark' | 'system'>('system');
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isFreePlan, setIsFreePlan] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [profileData, freePlanStatus] = await Promise.all([
          getUserProfile(),
          isUserOnFreePlan()
        ]);
        setProfile(profileData);
        setIsFreePlan(freePlanStatus);
      } catch (error) {
        console.error('Error fetching user data:', error);
      }
    };
    
    fetchData();
  }, []);

  const handleCopyLink = () => {
    navigator.clipboard.writeText(window.location.href);
    setShowCheck(true);
    setTimeout(() => setShowCheck(false), 2000); 
  }

  const openSettings = (tab: 'account' | 'api-key' | 'billing') => {
    setSettingsTab(tab);
    setShowSettings(true);
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
          {isShowChat ? (
            <>
              <Button variant="ghost" size="icon" onClick={handleCopyLink}>
                {showCheck ? (
                  <Check className="h-5 w-5" />
                ) : (
                  <Link className="h-5 w-5" />
                )}
                <span className="sr-only">Share</span>
              </Button>
            </>
          ) : (
            <>
              <Button variant="link" size="sm" onClick={() => router.push('https://docs.veyrax.com/')}>
                Docs
              </Button>
              <Button 
                variant="link" 
                size="sm"
                onClick={() => openSettings('api-key')}
              >
                API Key
              </Button>
            </>
          )}
          
          {isFreePlan && (
            <Button 
              variant="default" 
              size="sm"
              className="rounded-full"
              onClick={() => router.push('/pricing')}
            >
              Upgrade
            </Button>
          )}
          
          <div className="h-6 w-[1px] bg-border" />
          <UserDropdown 
            profile={profile}
            onOpenSettings={() => openSettings('account')}
          />
        </div>
      </header>

      <AccountSettingsDialog 
        open={showSettings} 
        onOpenChange={setShowSettings}
        initialTab={settingsTab}
      />
    </>
  );
}
