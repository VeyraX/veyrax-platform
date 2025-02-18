import { 
    FileText, 
    FileSpreadsheet, 
    FileImage, 
    FileVideo, 
    File,
    Calendar,
    NotebookText,
    Mail,
    LucideIcon 
  } from "lucide-react"
  
  export interface ToolCardIconConfig {
    icon: LucideIcon
    color: string
  }
  
  const MIME_TYPE_ICONS: Record<string, ToolCardIconConfig> = {
    'application/vnd.google-apps.document': {
      icon: FileText,
      color: 'text-blue-500'
    },
    'application/vnd.google-apps.spreadsheet': {
      icon: FileSpreadsheet,
      color: 'text-green-500'
    },
    'image/': {
      icon: FileImage,
      color: 'text-purple-500'
    },
    'video/': {
      icon: FileVideo,
      color: 'text-red-500'
    },
    'application/pdf': {
      icon: FileText,
      color: 'text-red-600'
    },
    'notion/page': {
      icon: NotebookText,
      color: 'text-slate-600'
    },
    'calendar/event': {
      icon: Calendar,
      color: 'text-blue-600'
    },
    'gmail/message': {
      icon: Mail,
      color: 'text-muted-foreground'
    }
  }
  
  const DEFAULT_ICON: ToolCardIconConfig = {
    icon: File,
    color: 'text-muted-foreground'
  }
  
  export function getToolCardIcon(type: string): ToolCardIconConfig {
    if (type in MIME_TYPE_ICONS) {
      return MIME_TYPE_ICONS[type]
    }
  
    const partialMatch = Object.keys(MIME_TYPE_ICONS).find(key => type.startsWith(key))
    if (partialMatch) {
      return MIME_TYPE_ICONS[partialMatch]
    }
  
    return DEFAULT_ICON
  }