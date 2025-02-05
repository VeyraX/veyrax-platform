'use client';

import React from 'react'
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarHeader,
  SidebarRail,
  SidebarGroupLabel,
} from "@/components/ui/sidebar"
import { useRouter } from "next/navigation"
import { usePathname } from "next/navigation"
import { endpoints } from "../../endpoint-dummydata"

interface EndpointsSidebarProps extends React.ComponentProps<typeof Sidebar> {
  currentEndpoint: string;
  onEndpointChange: (path: string) => void;
}

export function EndpointsSidebar({ currentEndpoint, onEndpointChange, ...props }: EndpointsSidebarProps) {
  const pathname = usePathname()
  const router = useRouter()

  return (
    <Sidebar collapsible="none" {...props}>
      
      <SidebarContent className='mt-2'>
        <SidebarGroup>
          <SidebarGroupLabel>Endpoints</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {endpoints.map((endpoint) => (
                <SidebarMenuItem key={endpoint.path} className='cursor-pointer'>
                  <SidebarMenuButton
                    asChild
                    isActive={currentEndpoint === endpoint.path}
                    onClick={() => {
                      onEndpointChange(endpoint.path);
                    }}
                  >
                    <div>
                      <span>{endpoint.path}</span>
                    </div>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
      <SidebarRail />
    </Sidebar>
  )
}
