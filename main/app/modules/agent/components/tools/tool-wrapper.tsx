import { useState } from 'react'
import { ChevronDown, ChevronRight } from 'lucide-react'
import { Button } from '@/components/ui/button'
import Image from 'next/image'

interface ToolWrapperProps {
  toolName: string
  children: React.ReactNode
}

const TOOL_CONFIGS = {
  gmail: {
    logo: '/logos/gmail-logo.svg',
    label: 'Gmail',
  },
  'google-calendar': {
    logo: '/logos/google-calendar-logo.svg',
    label: 'Google Calendar',
  },
  notion: {
    logo: '/logos/notion-logo.svg',
    label: 'Notion',
  },
  stripe: {
    logo: '/logos/stripe-logo.svg',
    label: 'Stripe',
  },
  openweather: {
    logo: '/logos/openweather-logo.png',
    label: 'OpenWeather',
  },
  perplexity: {
    logo: '/logos/perplexity-logo.svg',
    label: 'Perplexity',
  },
}

export function ToolWrapper({ toolName, children }: ToolWrapperProps) {
  const [isExpanded, setIsExpanded] = useState(true)
  const toolConfig = TOOL_CONFIGS[toolName as keyof typeof TOOL_CONFIGS]

  if (!toolConfig) return <>{children}</>

  return (
    <div className="border rounded-lg overflow-hidden">
      <div 
        className="flex items-center p-2 bg-accent/10 cursor-pointer hover:bg-accent/20"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <Button 
          variant="ghost" 
          size="sm" 
          className="h-6 w-6 p-0 mr-2"
          onClick={(e) => {
            e.stopPropagation()
            setIsExpanded(!isExpanded)
          }}
        >
          {isExpanded ? (
            <ChevronDown className="h-4 w-4" />
          ) : (
            <ChevronRight className="h-4 w-4" />
          )}
        </Button>
        
        <div className="flex items-center gap-2">
          <Image
            src={toolConfig.logo}
            alt={`${toolConfig.label} logo`}
            width={20}
            height={20}
            className="object-contain"
          />
          <span className="font-medium">{toolConfig.label}</span>
        </div>
      </div>
      
      {isExpanded && (
        <div className="p-4">
          {children}
        </div>
      )}
    </div>
  )
}