"use client"

import { useState, useEffect } from "react"
import { useTheme } from "next-themes"
import { usePathname } from "next/navigation"
import { Breadcrumb, BreadcrumbList, BreadcrumbItem, BreadcrumbLink, BreadcrumbSeparator } from "@/components/ui/breadcrumb"
import { Button } from "@/components/ui/button"
import { MoveRight } from "lucide-react"
import { useRouter } from "next/navigation"
import { createClient } from "@/lib/utils/supabase/client"

export function TopBarMenu() {
    const { theme, setTheme } = useTheme()
    const [mounted, setMounted] = useState(false)
    const [user, setUser] = useState<any>(null)
    const [loading, setLoading] = useState(true)
    const pathname = usePathname()
    const router = useRouter()

    useEffect(() => {
      const fetchUser = async () => {
        setLoading(true)
        const supabase = createClient()
        const { data: { session } } = await supabase.auth.getSession()
        setUser(session?.user || null)
        setLoading(false)
      }
      
      fetchUser()
      
      const supabase = createClient()
      const { data: { subscription } } = supabase.auth.onAuthStateChange(
        (_event, session) => {
          setUser(session?.user || null)
        }
      )
      
      return () => {
        subscription.unsubscribe()
      }
    }, [])

    const showEvenbright = pathname?.includes('/components/eventbright')

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
          {!loading && (
            <>
              {user ? (
                <Button 
                  variant="default" 
                  className="gap-2" 
                  size="sm"
                  onClick={() => router.push('/agent/new')}
                >
                  My Account
                  <MoveRight className="h-4 w-4" />
                </Button>
              ) : (
                <>
                  <Button 
                    variant="ghost" 
                    size="sm"
                    onClick={() => router.push('/login')}
                  >
                    Login
                  </Button>
                  <Button 
                    variant="default" 
                    size="sm"
                    onClick={() => router.push('/register')}
                  >
                    Register
                  </Button>
                </>
              )}
            </>
          )}
        </div>
      </nav>
    )
  }