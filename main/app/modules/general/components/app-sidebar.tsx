'use client';

import React, { useState, useEffect } from 'react'
import { Home, Library, Book, BookMarked, BookKey, ChevronUp, User2, Flag, Gift, Menu, LogOut, Loader2, Search, Glasses, Brain, Bot, Plug, FileText, LayoutGrid, LineChart, Palette, Paintbrush, ChevronDown, Settings, ChevronsUpDown, Component, Sparkles, ArrowRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import { createClientComponentClient } from '@supabase/auth-helpers-nextjs'
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarTrigger,
  useSidebar,
  SidebarHeader,
  SidebarFooter,
  SidebarMenuSub,
  SidebarMenuSubItem,
  SidebarMenuSubButton,
  SidebarGroupLabel,
  SidebarRail,
} from "@/components/ui/sidebar"
import { cn } from "@/lib/utils"
import { useRouter } from "next/navigation"
import { usePathname } from "next/navigation"
import { getChats } from "@/app/modules/agent/components/api/api.agent"
import { authApi } from '@/app/modules/auth/api/api.auth'

const items = [
  {
    title: "ACI",
    items: [
      {
        title: "Playground",
        url: "/agent",
      },
      {
        title: "ACI Generation",
        url: "/generate", 
      },
      {
        title: "Integrations",
        url: "/integrations",
      },
      {
        title: "Analytics",
        url: "",
      },
      {
        title: "Settings",
        url: "",
      },
    ],
  },
  {
    title: "Recent Chats",
    url: "/",
    items: [] // Initialize with empty array, will be populated by useEffect
  }
]

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  const pathname = usePathname()
  const router = useRouter()
  const { state } = useSidebar()
  const supabase = createClientComponentClient()
  const [chats, setChats] = useState<any[]>([])
  const [showAllChats, setShowAllChats] = useState(false)

  useEffect(() => {
    const fetchChats = async () => {
      try {
        const chats = await getChats();
        if (chats) {
          const chatItems = chats.map(chat => ({
            title: chat.name || 'Untitled Chat',
            url: `/agent/${chat.id}`
          }));
          
          items[1].items = chatItems;
          setChats(chats);
        }
      } catch (error) {
        console.error('Error fetching chats:', error);
      }
    };

    fetchChats();
  }, []);

  const handleLogoutClick = async () => {
    try {
      const { error } = await authApi.logout();
      if (error) throw error;
      router.refresh();
      router.push('/login');
    } catch (error) {
      console.error('Logout failed:', error);
    }
  }

  return (
    <>
      <Sidebar collapsible="icon" {...props}>
        <SidebarHeader>
          <div className="flex items-center gap-2 px-3 py-4">
            <img src="/logo.svg" alt="Logo" className="h-7 w-7" />
          </div>
        </SidebarHeader>
        <SidebarContent>

        {items.map((group) => (
            <SidebarGroup key={group.title}>
              <SidebarGroupLabel>{group.title}</SidebarGroupLabel>
              <SidebarGroupContent>
                <SidebarMenu>
                  {group.items?.slice(0, group.title === "Recent Chats" ? (showAllChats ? undefined : 5) : undefined).map((item) => (
                    <SidebarMenuItem className='cursor-pointer' key={item.title}>
                      <SidebarMenuButton
                        asChild
                        isActive={pathname === item.url}
                        onClick={() => router.push(item.url)}
                      >
                        <div>
                          <span>{item.title}</span>
                        </div>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  ))}
                  {group.title === "Recent Chats" && group.items && group.items.length > 5 && (
                    <SidebarMenuItem>
                      <Button
                        variant="link"
                        className="justify-start px-2 h-8"
                        onClick={() => setShowAllChats(!showAllChats)}
                      >
                        {showAllChats ? 'Show Less' : 'View All'}
                        {!showAllChats && <ArrowRight className="h-4 w-4" />}
                      </Button>
                    </SidebarMenuItem>
                  )}
                </SidebarMenu>
              </SidebarGroupContent>
            </SidebarGroup>
          ))}

        </SidebarContent>

        <SidebarFooter>
          <div className="flex items-center justify-start px-3 py-2">
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8"
              onClick={handleLogoutClick}
            >
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        </SidebarFooter>
        <SidebarRail />
      </Sidebar>
    </>
  )
}
