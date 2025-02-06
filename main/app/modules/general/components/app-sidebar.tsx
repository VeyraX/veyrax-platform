'use client';

import React, { useState, useEffect } from 'react'
import { Home, Library, Book, BookMarked, BookKey, ChevronUp, User2, Flag, Gift, Menu, LogOut, Loader2, Search, Glasses, Brain, Bot, Plug, FileText, LayoutGrid, LineChart, Palette, Paintbrush, ChevronDown, Settings, ChevronsUpDown, Component, Sparkles } from "lucide-react"
import { Button } from "@/components/ui/button"
import { HandleLogout } from "@/lib/actions/actions"
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
        title: "Integrations",
        url: "",
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
  }
]

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  const pathname = usePathname()
  const router = useRouter()
  const { state } = useSidebar()

  const handleLogoutClick = async () => {
    try {
      await HandleLogout()
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
                  {group.items.map((item) => (
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

