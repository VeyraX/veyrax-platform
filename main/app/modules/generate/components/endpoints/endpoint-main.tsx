"use client"

import { useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import type { EndpointData } from "../../endpoint-types"
import Api from "./endpoint-api"
import EndpointCodeMain from "./endpoint-code/endpoint-code-main"
import Preview from "./endpoint-preview"

interface EndpointViewProps {
  data: EndpointData
  path: string
}

export default function EndpointView({ data, path }: EndpointViewProps) {
  const [activeLowTab, setActiveLowTab] = useState("API")
  const [hoveredLowTab, setHoveredLowTab] = useState<number | null>(null)

  const lowTabs = ["API", "Code", "Preview"]

  return (
    <div>
      <div className="mb-4 p-3 bg-[#0e0f1114] dark:bg-[#ffffff0a] rounded-md">
        <code className="text-sm font-mono">npx veyrax add {path}</code>
      </div>

      <div className="relative mb-4">
        <div
          className="absolute h-[30px] transition-all duration-300 ease-out bg-[#0e0f1114] dark:bg-[#ffffff1a] rounded-[6px]"
          style={{
            left: hoveredLowTab !== null ? `${hoveredLowTab * 80}px` : "0",
            width: "80px",
            opacity: hoveredLowTab !== null ? 1 : 0,
          }}
        />
        <div
          className="absolute bottom-[-6px] h-[2px] bg-[#0e0f11] dark:bg-white transition-all duration-300 ease-out"
          style={{
            left: `${lowTabs.indexOf(activeLowTab) * 80}px`,
            width: "80px",
          }}
        />
        <div className="relative flex space-x-[6px] items-center">
          {lowTabs.map((tab, index) => (
            <div
              key={index}
              className={`px-3 py-2 cursor-pointer transition-colors duration-300 h-[30px] w-[80px] ${
                tab === activeLowTab ? "text-[#0e0e10] dark:text-white" : "text-[#0e0f1199] dark:text-[#ffffff99]"
              }`}
              onMouseEnter={() => setHoveredLowTab(index)}
              onMouseLeave={() => setHoveredLowTab(null)}
              onClick={() => setActiveLowTab(tab)}
            >
              <div className="text-sm font-[var(--www-mattmannucci-me-geist-regular-font-family)] leading-5 whitespace-nowrap flex items-center justify-center h-full">
                {tab}
              </div>
            </div>
          ))}
        </div>
      </div>

      <Card>
        <CardContent className="p-4">
          {activeLowTab === "API" && <Api data={data} />}
          {activeLowTab === "Code" && <EndpointCodeMain data={data} />}
          {activeLowTab === "Preview" && <Preview data={data} />}
        </CardContent>
      </Card>
    </div>
  )
}

