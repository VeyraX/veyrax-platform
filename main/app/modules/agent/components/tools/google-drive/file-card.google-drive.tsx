// Карточка для обычных файлов в стиле EventCard
import { 
  File, 
  ExternalLink, 
  FileText,
  FileSpreadsheet,
  FileImage,
  FileArchive,
  FileCode,
  FileVideo,
  FileAudio,
  FileChartPie,
} from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { DriveFile } from "./types.google-drive"
import { formatDistanceToNow } from "date-fns"

const getFileIcon = (mimeType: string) => {
  switch (mimeType) {
    case 'application/vnd.google-apps.document':
      return <FileText className="h-4 w-4 text-blue-500 flex-shrink-0" />
    case 'application/vnd.google-apps.spreadsheet':
      return <FileSpreadsheet className="h-4 w-4 text-green-500 flex-shrink-0" />
    case 'application/vnd.google-apps.presentation':
      return <FileChartPie className="h-4 w-4 text-yellow-500 flex-shrink-0" />
    case 'application/vnd.google-apps.form':
      return <FileText className="h-4 w-4 text-purple-500 flex-shrink-0" />
    case 'application/pdf':
      return <FileText className="h-4 w-4 text-red-500 flex-shrink-0" />
    case 'image/jpeg':
    case 'image/png':
    case 'image/gif':
      return <FileImage className="h-4 w-4 text-purple-500 flex-shrink-0" />
    case 'application/zip':
    case 'application/x-rar-compressed':
      return <FileArchive className="h-4 w-4 text-orange-500 flex-shrink-0" />
    case 'text/javascript':
    case 'text/css':
    case 'text/html':
      return <FileCode className="h-4 w-4 text-emerald-500 flex-shrink-0" />
    case 'video/mp4':
    case 'video/quicktime':
      return <FileVideo className="h-4 w-4 text-pink-500 flex-shrink-0" />
    case 'audio/mpeg':
    case 'audio/wav':
      return <FileAudio className="h-4 w-4 text-indigo-500 flex-shrink-0" />
    default:
      return <File className="h-4 w-4 text-muted-foreground flex-shrink-0" />
  }
}

interface FileCardProps {
  file: DriveFile
}

export function FileCard({ file }: FileCardProps) {
  const formattedDate = file.modified_time 
    ? formatDistanceToNow(new Date(file.modified_time), { addSuffix: true })
    : 'Unknown date';

  return (
    <Card className="w-[300px] inline-block mr-3">
      <CardContent className="p-3 flex flex-col">
        <div className="flex items-center justify-between gap-2 mb-2">
          <div className="flex items-center gap-2 flex-1 min-w-0">
            {getFileIcon(file.mime_type)}
            <span className="truncate text-sm font-medium">{file.name}</span>
          </div>
          {file.web_view_link && (
            <a
              href={file.web_view_link}
              target="_blank"
              rel="noopener noreferrer"
              className="text-muted-foreground hover:text-foreground"
            >
              <ExternalLink className="h-4 w-4 flex-shrink-0" />
            </a>
          )}
        </div>
        <div className="text-xs text-muted-foreground">
          {formattedDate}
        </div>
      </CardContent>
    </Card>
  )
}

export function FileCardSkeleton() {
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