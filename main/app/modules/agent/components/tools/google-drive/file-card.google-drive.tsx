import { ToolCard } from "../common/tool-card"
import { DriveFile } from "./types.google-drive"
import { formatDistanceToNow } from "date-fns"

interface FileCardProps {
  file: DriveFile
}

export function FileCard({ file }: FileCardProps) {
  const formattedDate = file.modified_time 
    ? formatDistanceToNow(new Date(file.modified_time), { addSuffix: true })
    : 'Unknown date';

  return (
    <ToolCard
      resourceType={file.mime_type}
      title={file.name}
      subtitle={formattedDate}
      externalLink={file.web_view_link}
    />
  )
}

export { ToolCardSkeleton as FileCardSkeleton } from "../common/tool-card"