'use client';

import React, { useState, useEffect } from 'react'
import { Home, Library, Book, BookMarked, BookKey, ChevronUp, User2, Flag, Gift, Menu, Loader2, Search, Glasses, Brain, Plug, FileText, LayoutGrid, LineChart, Palette, Paintbrush, ChevronDown, Settings, ChevronsUpDown, Component, ArrowRight, MessageSquare, X, Play } from "lucide-react"
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
import { TerminalIcon as Terminal } from "@/components/ui/terminal"
import { Card } from "@/components/ui/card"
import { Dialog, DialogContent } from "@/components/ui/dialog"
import { FlowsAnnouncement } from "./flows-announcement"

const items = [
  {
    title: "Connect",
    items: [
      {
        title: "Integrations",
        url: "/integrations",
        icon: <Connect size={16} />,
      },
      {
        title: "Deployment",
        url: "/deployment/create",
        icon: <Terminal size={16} />,
      },
    ],
  },
  {
    title: "Build",
    items: [
      {
        title: "Playground",
        url: "/agent",
        icon: <Sparkles size={16} />,
      },
      {
        title: "Flows",
        url: "/flows",
        icon: <Layers size={16} />,
      },
    ],
  },
  {
    title: "Feedback",
    items: [
      {
        title: "Give Feedback",
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

function Announcement() {
  const [isVisible, setIsVisible] = useState(false);
  const [videoDialogOpen, setVideoDialogOpen] = useState(false);

  useEffect(() => {
    const isAnnoucementClosed = localStorage.getItem('flowsAnnouncementClosed');
    if (!isAnnoucementClosed) {
      setIsVisible(true);
    }
  }, []);

  const handleClose = () => {
    setIsVisible(false);
    localStorage.setItem('flowsAnnouncementClosed', 'true');
  };

  return isVisible ? (
    <>
      <Card className="p-4 mx-3 mb-4 relative">
        <Button
          variant="ghost"
          size="icon"
          className="absolute right-2 top-2 h-6 w-6"
          onClick={handleClose}
        >
          <X className="h-4 w-4" />
        </Button>
        
        <h4 className="font-semibold mb-2">Announcing Flows</h4>
        <p className="text-sm text-muted-foreground mb-3">
          Create any workflow you want with our new Flows feature
        </p>
        
        <div 
          className="relative rounded-md overflow-hidden bg-secondary cursor-pointer"
          onClick={() => setVideoDialogOpen(true)}
        >
          <div className="absolute inset-0 flex items-center justify-center bg-black/20">
            <Play className="h-8 w-8 text-white" />
          </div>
          <img 
            src="/flows-preview.jpg" 
            alt="Flows Preview" 
            className="w-full h-[120px] object-cover"
          />
        </div>
      </Card>

      <Dialog open={videoDialogOpen} onOpenChange={setVideoDialogOpen}>
        <DialogContent className="sm:max-w-[800px]">
          <div className="aspect-video">
            <iframe
              width="100%"
              height="100%"
              src="https://www.youtube.com/embed/your-video-id"
              title="Flows Announcement"
              frameBorder="0"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
            />
          </div>
        </DialogContent>
      </Dialog>
    </>
  ) : null;
}

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
      
      items[3].items = chatItems as any;
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
                  {(state === "expanded" || group.title !== "Recent Chats") && 
                    group.items?.slice(0, group.title === "Recent Chats" ? (showAllChats ? undefined : 5) : undefined).map((item) => (
                      <SidebarMenuItem className='cursor-pointer' key={item.title}>
                        <SidebarMenuButton
                          asChild
                          isActive={Boolean(pathname === item.url || (item.url && pathname.startsWith(item.url)))}
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

        <FlowsAnnouncement />

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
