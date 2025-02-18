import { Command, CommandGroup, CommandItem } from "@/components/ui/command"
import { Mail, Calendar, FileText, Cloud, Book, Globe } from "lucide-react"

import { ReactNode } from "react"

export interface Tool {
    id: string
    name: string
    description: string
    icon?: ReactNode
  }

const TOOLS: Tool[] = [
  {
    id: 'gmail',
    name: 'Gmail',
    description: 'Search and manage your emails',
    icon: <Mail className="w-4 h-4" />
  },
  {
    id: 'calendar',
    name: 'Calendar',
    description: 'Manage your calendar and events',
    icon: <Calendar className="w-4 h-4" />
  },
  {
    id: 'drive',
    name: 'Google Drive',
    description: 'Access and manage your files',
    icon: <FileText className="w-4 h-4" />
  },
  {
    id: 'notion',
    name: 'Notion',
    description: 'Work with your Notion workspace',
    icon: <Book className="w-4 h-4" />
  },
  {
    id: 'linear',
    name: 'Linear',
    description: 'Manage issues and projects',
    icon: <Cloud className="w-4 h-4" />
  },
  {
    id: 'weather',
    name: 'Weather',
    description: 'Check weather conditions',
    icon: <Globe className="w-4 h-4" />
  }
]

interface CommandPaletteProps {
  isOpen: boolean
  onClose: () => void
  onSelect: (toolId: string) => void
  filterValue: string
}

export function CommandPalette({ 
  isOpen, 
  onClose, 
  onSelect,
  filterValue 
}: CommandPaletteProps) {
  if (!isOpen) return null

  return (
    <Command className="absolute bottom-full mb-1 w-full rounded-lg border shadow-md z-50">
      <CommandGroup heading="Available Tools">
        {TOOLS.filter(tool => 
          tool.name.toLowerCase().includes(filterValue.toLowerCase()) ||
          tool.description.toLowerCase().includes(filterValue.toLowerCase())
        ).map(tool => (
          <CommandItem
            key={tool.id}
            onSelect={() => onSelect(tool.id)}
            className="flex items-center gap-2 px-2 py-1.5"
          >
            {tool.icon}
            <div>
              <p className="font-medium">{tool.name}</p>
              <p className="text-sm text-muted-foreground">{tool.description}</p>
            </div>
          </CommandItem>
        ))}
      </CommandGroup>
    </Command>
  )
}