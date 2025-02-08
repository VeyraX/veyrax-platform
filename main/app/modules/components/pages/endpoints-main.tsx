"use client"

import { useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { endpoints, endpointsData } from "../endpoint-dummydata"
import EndpointView from "../components/endpoints/endpoint-main"
import { EndpointsSidebar } from "../components/endpoints/endpoints-sidebar"
import { Button } from "@/components/ui/button"
import { useRouter } from "next/navigation"
import { toast } from "sonner"

interface GeneratePageProps {
  isPreview?: boolean
}

export default function GeneratePage({ isPreview = false }: GeneratePageProps) {
  const [isDarkMode, setIsDarkMode] = useState(false)
  const [activeEndpoint, setActiveEndpoint] = useState(endpoints[0].path)
  const router = useRouter()
  return (
    <div className={`flex w-full h-screen ${isDarkMode ? "dark bg-[#0e0f11]" : ""}`}>
      <EndpointsSidebar 
        currentEndpoint={activeEndpoint} 
        onEndpointChange={setActiveEndpoint}
        className="hidden lg:block h-full"
      />
      
      <div className="flex-1 h-full overflow-auto">
        <Card className={`w-full h-full border-none shadow-none ${isDarkMode ? "bg-transparent" : ""}`}>
          <CardContent className="p-4">
            <div className="flex justify-between items-start">
              <EndpointView data={endpointsData[activeEndpoint]} path={activeEndpoint} isPreview={isPreview} />
              {isPreview && (
                <Button 
                  variant="outline" 
                  onClick={() => {
                    router.push(`/components`)
                    toast.success("Successfully published!")
                  }}
                >
                  Publish
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

