'use client'

import AssistantPage from "@/app/modules/agent/pages/assistant-page"
import { useParams } from "next/navigation"

export default function AgentPage() {
  const params = useParams<{ id?: string[] }>()
  const chatId = params.id?.[0] || 'new'
  
  return <AssistantPage params={{ chatId }} />
}