"use client"

import { useState } from "react"
import { useTheme } from "next-themes"
import { usePathname } from "next/navigation"
import { Breadcrumb, BreadcrumbList, BreadcrumbItem, BreadcrumbLink, BreadcrumbSeparator } from "@/components/ui/breadcrumb"
import { Button } from "@/components/ui/button"
import { Sun, Moon, MoveRight, ArrowUp } from "lucide-react"
import { useRouter } from "next/navigation"
import { WaitlistDialog } from "@/app/modules/landing/components/web/waitlist-dialog"
import { BetaDialog } from "@/app/modules/landing/components/agent/beta-dialog"


export function TopBarMenu() {
    const { theme, setTheme } = useTheme()
    const [mounted, setMounted] = useState(false)
    const [user, setUser] = useState<any>(null)
    const pathname = usePathname()
    const router = useRouter()

    const showEvenbright = pathname?.includes('/components/eventbright')
    const showBetaButton = pathname?.includes('/web/agent')

    return (
      <nav className="flex h-14 w-full items-center justify-between border-b px-6">
        <div className="flex items-center gap-4">
          <img 
            src="/logo.svg"
            alt="Logo"
            className="w-7 h-7 cursor-pointer" 
            onClick={() => router.push('/web')}
          />
          
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
            <>
              {showBetaButton ? (
                <BetaDialog 
                  trigger={
                    <Button 
                      variant="default" 
                      className="rounded-full transition-all duration-200 ease-in-out hover:bg-white hover:text-black dark:hover:bg-black dark:hover:text-white"
                      size="sm"
                    >
                      Join Beta
                      <ArrowUp className="w-4 h-4 relative z-10" />
                    </Button>
                  }
                />
              ) : (
                <WaitlistDialog 
                  trigger={
                    <Button variant="default" className="gap-2" size="sm">
                      Join Waitlist <MoveRight className="h-4 w-4" />
                    </Button>
                  }
                />
              )}
            </>
          )}
        </div>
      </nav>
    )
  }