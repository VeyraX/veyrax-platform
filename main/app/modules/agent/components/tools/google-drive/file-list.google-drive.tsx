import { Folder, File, ChevronDown, ChevronRight, ExternalLink } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { useState } from "react"
import { DriveFile } from "./types.google-drive"
import { formatDistanceToNow } from "date-fns"
import { FileCard } from "./file-card.google-drive"

interface FileListProps {
  files: DriveFile[]
}

function FolderGroup({ name, files }: { name: string, files: DriveFile[] }) {
  const [isExpanded, setIsExpanded] = useState(false)

  return (
    <div className="border-b border-border hover:shadow-sm transition-shadow">
      <div 
        className="flex items-center px-4 py-2 cursor-pointer hover:bg-accent/50"
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
        
        <div className="flex-1 grid grid-cols-12 gap-4 items-center min-w-0">
          <div className="col-span-9 flex items-center gap-2 truncate">
            <Folder className="h-4 w-4 text-muted-foreground flex-shrink-0" />
            <span className="truncate font-medium">{name}</span>
          </div>
          <div className="col-span-3 text-right text-sm text-muted-foreground">
            {files.length} files
          </div>
        </div>
      </div>

      {isExpanded && (
        <div className="px-12 py-4 bg-accent/20">
          <div className="flex flex-wrap gap-4">
            {files.map(file => (
              <FileCard key={file.id} file={file} />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export function FileList({ files }: FileListProps) {
  const groupedFiles = files.reduce((acc, file) => {
    const parentName = file.parent_names?.[0] || 'Root'
    if (!acc[parentName]) {
      acc[parentName] = []
    }
    acc[parentName].push(file)
    return acc
  }, {} as Record<string, DriveFile[]>)

  return (
    <div className="space-y-4">
      {Object.entries(groupedFiles).map(([parentName, files]) => (
        <FolderGroup key={parentName} name={parentName} files={files} />
      ))}
    </div>
  )
}

export function FileListSkeleton() {
  return (
    <div className="border-b border-border px-4 py-2">
      <div className="flex items-center">
        <Skeleton className="h-4 w-4 mr-2" />
        <div className="flex-1 grid grid-cols-12 gap-4">
          <div className="col-span-9">
            <Skeleton className="h-4 w-48" />
          </div>
          <div className="col-span-3">
            <Skeleton className="h-4 w-24 ml-auto" />
          </div>
        </div>
      </div>
    </div>
  )
}