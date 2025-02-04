import type React from "react"

export interface Endpoint {
  path: string
  method: string
}

export interface EndpointData {
  method: string
  description: string
  inputSchema: object
  responseSchema: object
  preview: React.ReactNode
  code: Array<{
    snippet: string
    path: string
  }>
}

export interface EndpointsData {
  [key: string]: EndpointData
}

