'use client';

import React, { useState, useEffect } from 'react'
import { Home, Library, Book, BookMarked, BookKey, ChevronUp, User2, Flag, Gift, Menu, Loader2, Search, Glasses, Brain, Plug, FileText, LayoutGrid, LineChart, Palette, Paintbrush, ChevronDown, Settings, ChevronsUpDown, Component, ArrowRight, MessageSquare } from "lucide-react"
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
import { getChats } from "@/app/modules/agent/api/api.agent"
import { authApi } from '@/app/modules/auth/api/api.auth'
import { useGetChats } from "@/app/modules/agent/api/quries.agent"
import FeedbackDialog from './feedback-dialog'
import { LogoutIcon as Logout } from "@/components/ui/logout"
import { BoxesIcon as Boxes } from "@/components/ui/boxes"
import { HandHeartIcon as HandHeart } from "@/components/ui/hand-heart"
import { SparklesIcon as Sparkles } from "@/components/ui/sparkles"
import { DiscordIcon as Discord } from "@/components/ui/discord"
import { WorkflowIcon as Workflow } from "@/components/ui/workflow"
import { LayersIcon as Layers } from "@/components/ui/layers"
import { ConnectIcon as Connect } from "@/components/ui/connect"

const items = [
  {
    title: "ACI",
    items: [
      {
        title: "Playground",
        url: "/agent",
        icon: <Sparkles size={16} />,
      },
      {
        title: "Integrations",
        url: "/integrations",
        icon: <Connect size={16} />,
      },
      {
        title: "Feedback",
        action: "feedback",
        icon: <HandHeart size={16} />,
      },
      {
        title: "Join Discord",
        action: "discord",
        url: "https://discord.gg/s8FPCADUTd",
        icon: <Discord size={16} />,
      },
    ],
  },
  {
    title: "Recent Chats",
    url: "/",
    items: []
  }
]

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  const pathname = usePathname()
  const router = useRouter()
  const { state } = useSidebar()
  const supabase = createClientComponentClient()
  const [chats, setChats] = useState<any[]>([])
  const [showAllChats, setShowAllChats] = useState(false)
  const [mounted, setMounted] = useState(false)
  const { data: chatData } = useGetChats()
  const [feedbackDialogOpen, setFeedbackDialogOpen] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  useEffect(() => {
    if (mounted && chatData) {
      const chatItems = chatData.map((chat: any) => ({
        title: chat.name || 'Untitled Chat',
        url: `/agent/${chat.id}`
      }));
      
      items[1].items = chatItems as any;
      setChats(chatData);
    }
  }, [mounted, chatData]);

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

  const handleItemClick = (item: any) => {
    if (item.action === 'feedback') {
      setFeedbackDialogOpen(true);
    } else if (item.action === 'discord') {
      window.open(item.url, '_blank');
    } else if (item.url) {
      router.push(item.url);
    }
  }

  if (!mounted) return null;

  return (
    <>
      <Sidebar collapsible="icon" {...props}>
        <SidebarHeader>
          <div className={cn(
            "flex items-center gap-2 px-3 py-4",
            "group-data-[collapsible=icon]:justify-center group-data-[collapsible=icon]:px-0"
          )}>
            <img 
              src="/logo.svg" 
              alt="Logo" 
              className={cn(
                "h-8 w-8",
                "group-data-[collapsible=icon]:h-7 group-data-[collapsible=icon]:w-7"
              )} 
            />
          </div>
        </SidebarHeader>
        <SidebarContent>
          {items.map((group) => (
            <SidebarGroup key={group.title}>
              <SidebarGroupLabel>{group.title}</SidebarGroupLabel>
              <SidebarGroupContent>
                <SidebarMenu>
                  {(state === "expanded" || group.title === "ACI") && 
                    group.items?.slice(0, group.title === "Recent Chats" ? (showAllChats ? undefined : 5) : undefined).map((item) => (
                      <SidebarMenuItem className='cursor-pointer' key={item.title}>
                        <SidebarMenuButton
                          asChild
                          isActive={pathname === item.url}
                          onClick={() => handleItemClick(item)}
                          tooltip={item.title}
                        >
                          <div>
                            {item.icon}
                            <span>{item.title}</span>
                          </div>
                        </SidebarMenuButton>
                      </SidebarMenuItem>
                    ))}
                  {state === "expanded" && group.title === "Recent Chats" && group.items && group.items.length > 5 && (
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
          <div className="flex items-center justify-start">
            <SidebarMenuItem className="marker:content-none list-none">
              <SidebarMenuButton
                asChild
                tooltip="Logout"
                onClick={handleLogoutClick}
              >
                <div>
                  <Logout size={16} />
                </div>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </div>
        </SidebarFooter>
        <SidebarRail />
      </Sidebar>
      
      <FeedbackDialog 
        open={feedbackDialogOpen} 
        onOpenChange={setFeedbackDialogOpen} 
      />
    </>
  )
}
