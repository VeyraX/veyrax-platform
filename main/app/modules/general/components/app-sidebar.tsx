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
    items: [
      {
        title: "Project Brainstorming",
        url: "/chat/1",
      },
      {
        title: "Marketing Strategy", 
        url: "/chat/2",
      },
      {
        title: "Product Research",
        url: "/chat/3", 
      },
      {
        title: "Customer Feedback Analysis",
        url: "/chat/4",
      },
      {
        title: "Team Planning",
        url: "/chat/5",
      },
      {
        title: "Feature Development", 
        url: "/chat/6",
      },
      {
        title: "User Experience Review",
        url: "/chat/7",
      },
      {
        title: "Content Strategy",
        url: "/chat/8",
      },
    ],
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
    // Fetch chats from API/database
    const fetchChats = async () => {
      try {
        const { data: chats } = await supabase
          .from('chats')
          .select('*')
          .order('created_at', { ascending: false })
          .limit(8)
        
        if (chats) {
          items[1].items = chats.map(chat => ({
            title: chat.title || `Chat ${chat.id}`,
            url: `/chat/${chat.id}`
          }))
          setChats(chats)
        }
      } catch (error) {
        console.error('Error fetching chats:', error)
      }
    }

    fetchChats()
  }, [])

  const handleLogoutClick = async () => {
    try {
      await supabase.auth.signOut()
      router.refresh()
      router.push('/login')
    } catch (error) {
      console.error('Logout failed:', error)
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
