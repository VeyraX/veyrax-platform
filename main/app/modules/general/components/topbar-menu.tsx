"use client"

import { useState } from "react"
import { useTheme } from "next-themes"
import { usePathname } from "next/navigation"
import { Breadcrumb, BreadcrumbList, BreadcrumbItem, BreadcrumbLink, BreadcrumbSeparator } from "@/components/ui/breadcrumb"
import { Button } from "@/components/ui/button"
import { Sun, Moon } from "lucide-react"
import { useRouter } from "next/navigation"


export function TopBarMenu() {
    const { theme, setTheme } = useTheme()
    const [mounted, setMounted] = useState(false)
    const [user, setUser] = useState<any>(null)
    const pathname = usePathname()
    const router = useRouter()

    const showEvenbright = pathname?.includes('/components/eventbright')

    return (
      <nav className="flex h-14 w-full items-center justify-between border-b px-6">
        <div className="flex items-center gap-4">
          <div className="w-6 h-6 rounded-full bg-black dark:bg-white" />
          
          {showEvenbright && (
            <Breadcrumb>
              <BreadcrumbList>
                <BreadcrumbSeparator />
                <BreadcrumbItem>
                  <BreadcrumbLink href="/Evenbright">
                    Evenbright
                  </BreadcrumbLink>
                </BreadcrumbItem>
              </BreadcrumbList>
            </Breadcrumb>
          )}
        </div>
  
        <div className="flex items-center gap-2">
          {user ? (
            <div className="flex items-center gap-2">
              <span className="text-sm">{user.email}</span>
            </div>
          ) : (
            <Button 
              variant="default" 
              onClick={() => router.push('/waitlist')}
            >
              Join Waitlist
            </Button>
          )}
        </div>
      </nav>
    )
  }