import { ExternalLink } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { getToolCardIcon } from "./tool-card-icon-color"

export interface ToolCardProps {
  resourceType: string
  title: string
  subtitle?: string
  externalLink?: string
}

export function ToolCard({ 
  resourceType,
  title, 
  subtitle,
  externalLink 
}: ToolCardProps) {
  const { icon: Icon, color } = getToolCardIcon(resourceType)

  return (
    <Card className="w-[300px] inline-block mr-3">
      <CardContent className="p-3 flex flex-col">
        <div className="flex items-center justify-between gap-2 mb-2">
          <div className="flex items-center gap-2 flex-1 min-w-0">
            <Icon className={`h-4 w-4 flex-shrink-0 ${color}`} />
            <span className="truncate text-sm font-medium">{title}</span>
          </div>
          {externalLink && (
            <a
              href={externalLink}
              target="_blank"
              rel="noopener noreferrer"
              className="text-muted-foreground hover:text-foreground"
            >
              <ExternalLink className="h-4 w-4 flex-shrink-0" />
            </a>
          )}
        </div>
        {subtitle && (
          <div className="text-xs text-muted-foreground">
            {subtitle}
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export function ToolCardSkeleton() {
  return (
    <Card className="w-[300px] inline-block mr-3">
      <CardContent className="p-3 flex flex-col">
        <div className="flex items-center justify-between gap-2 mb-2">
          <div className="flex items-center gap-2 flex-1 min-w-0">
            <Skeleton className="h-4 w-4 flex-shrink-0" />
            <Skeleton className="h-4 w-3/4" />
          </div>
          <Skeleton className="h-4 w-4 flex-shrink-0" />
        </div>
        <Skeleton className="h-3 w-1/2" />
      </CardContent>
    </Card>
  )
}