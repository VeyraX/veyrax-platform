import React, { useState } from 'react';
import { Settings, CreditCard, MoonStar, Sun, Monitor, LogOut } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { UserProfile } from '@/app/modules/settings/api/types.settings';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useTheme } from "next-themes"
import { authApi } from '@/app/modules/auth/api/api.auth'
import { useRouter } from 'next/navigation'

interface UserDropdownProps {
  profile: UserProfile | null;
  onOpenSettings: () => void;
}

export function UserDropdown({ profile, onOpenSettings }: UserDropdownProps) {
  const { theme, setTheme } = useTheme()
  const router = useRouter()

  const handleLogout = async () => {
    try {
      const { error } = await authApi.logout();
      if (error) throw error;
      router.refresh();
      router.push('/login');
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button 
          variant="ghost" 
          size="icon" 
          className="p-0"
        >
          <Avatar className="h-8 w-8">
            {profile?.avatar_url ? (
              <AvatarImage
                src={profile.avatar_url}
                alt={profile?.full_name ?? 'Profile picture'}
              />
            ) : null}
            <AvatarFallback>
              {profile?.full_name 
                ? profile.full_name.split(' ').map(n => n[0]).join('')
                : 'U'}
            </AvatarFallback>
          </Avatar>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-[240px]">
        <div className="flex items-center gap-2 p-2">
          <Avatar className="h-8 w-8">
            <AvatarImage src={profile?.avatar_url ?? ''} />
            <AvatarFallback>
              {profile?.full_name 
                ? profile.full_name.split(' ').map(n => n[0]).join('')
                : 'U'}
            </AvatarFallback>
          </Avatar>
          <div className="flex flex-col">
            <span className="text-sm font-medium leading-none">{profile?.full_name}</span>
            <span className="text-xs text-muted-foreground mt-1">{profile?.email}</span>
          </div>
        </div>
        <DropdownMenuSeparator />
        <div className="py-1.5">
          <DropdownMenuItem onClick={onOpenSettings} className="py-2">
            <span className="text-sm">Account settings</span>
            <Settings className="ml-auto h-4 w-4" />
          </DropdownMenuItem>
          <DropdownMenuItem className="py-2">
            <span className="text-sm">Manage subscription</span>
            <CreditCard className="ml-auto h-4 w-4" />
          </DropdownMenuItem>
        </div>
        <DropdownMenuSeparator />
        <div className="py-2">
          <div className="text-sm font-medium px-2 mb-2">Theme</div>
          <div className="px-2">
            <Tabs value={theme} onValueChange={setTheme}>
              <TabsList className="w-full">
                <TabsTrigger value="light" className="flex-1 px-0 py-1.5">
                  <Sun className="h-4 w-4" />
                </TabsTrigger>
                <TabsTrigger value="dark" className="flex-1 px-0 py-1.5">
                  <MoonStar className="h-4 w-4" />
                </TabsTrigger>
                <TabsTrigger value="system" className="flex-1 px-0 py-1.5">
                  <Monitor className="h-4 w-4" />
                </TabsTrigger>
              </TabsList>
            </Tabs>
          </div>
        </div>
        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={handleLogout} className="py-2">
          <span className="text-sm">Log out</span>
          <LogOut className="ml-auto h-4 w-4" />
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}