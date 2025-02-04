"use client"

import { useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { endpoints, endpointsData } from "../endpoint-dummydata"
import EndpointView from "../components/endpoints/endpoint-main"

export default function GeneratePage() {
  const [isDarkMode, setIsDarkMode] = useState(false)
  const [activeEndpoint, setActiveEndpoint] = useState(endpoints[0].path)
  const [hoveredHighTab, setHoveredHighTab] = useState<number | null>(null)

  const toggleDarkMode = () => {
    setIsDarkMode(!isDarkMode)
    document.documentElement.classList.toggle("dark")
  }

  return (
    <div className={`flex flex-col items-center w-full min-h-screen p-4 ${isDarkMode ? "dark bg-[#0e0f11]" : ""}`}>
      <Card className={`w-full max-w-[1200px] border-none shadow-none ${isDarkMode ? "bg-transparent" : ""}`}>
        <CardContent className="p-4">
          <div className="flex justify-between items-center mb-4">
            <h1 className="text-2xl font-bold">API Documentation</h1>
          </div>

          <div className="relative mb-4">
            <div
              className="absolute h-[30px] transition-all duration-300 ease-out bg-[#0e0f1114] dark:bg-[#ffffff1a] rounded-[6px]"
              style={{
                left: hoveredHighTab !== null ? `${hoveredHighTab * 120}px` : "0",
                width: "120px",
                opacity: hoveredHighTab !== null ? 1 : 0,
              }}
            />
            <div
              className="absolute bottom-[-6px] h-[2px] bg-[#0e0f11] dark:bg-white transition-all duration-300 ease-out"
              style={{
                left: `${endpoints.findIndex((e) => e.path === activeEndpoint) * 120}px`,
                width: "120px",
              }}
            />
            <div className="relative flex items-center">
              {endpoints.map((endpoint, index) => (
                <div
                  key={index}
                  className={`px-3 py-2 cursor-pointer transition-colors duration-300 h-[30px] w-[120px] ${
                    endpoint.path === activeEndpoint
                      ? "text-[#0e0e10] dark:text-white"
                      : "text-[#0e0f1199] dark:text-[#ffffff99]"
                  }`}
                  onMouseEnter={() => setHoveredHighTab(index)}
                  onMouseLeave={() => setHoveredHighTab(null)}
                  onClick={() => setActiveEndpoint(endpoint.path)}
                >
                  <div className="text-sm font-[var(--www-mattmannucci-me-geist-regular-font-family)] leading-5 whitespace-nowrap flex items-center justify-center h-full">
                    {endpoint.path}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Endpoint View */}
          <EndpointView data={endpointsData[activeEndpoint]} path={activeEndpoint} />
        </CardContent>
      </Card>
    </div>
  )
}

