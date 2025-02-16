import type React from "react"
import Link from "next/link"
import { formatDistanceToNow } from "date-fns"
import type { Page } from "./types.notion"
import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { FileTextIcon, ExternalLink } from "lucide-react"
import { Skeleton } from "@/components/ui/skeleton"
import { Table, TableHeader, TableBody, TableCell, TableRow, TableHead } from "@/components/ui/table"
import { Database } from "./types.notion"
type NotionPageListProps = {
  pages: Page[] | undefined;
}

export const NotionPageList: React.FC<NotionPageListProps> = ({ pages }) => {
  return (
    <div className="container mx-auto p-4">
      <div className="flex flex-wrap gap-4">
        {pages?.map((page, index) => (
          <Card key={index} className="w-[300px]">
            <CardContent className="p-3 flex flex-col">
              <div className="flex items-center justify-between gap-2 mb-2">
                <div className="flex items-center gap-2 flex-1 min-w-0">
                  <FileTextIcon className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                  <span className="truncate text-sm font-medium">{page.title}</span>
                </div>
                <Link
                  href={page.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-muted-foreground hover:text-foreground"
                >
                  <ExternalLink className="h-4 w-4 flex-shrink-0" />
                </Link>
              </div>
              <div className="text-xs text-muted-foreground space-y-1">
                <div>Edited {formatDistanceToNow(new Date(page.last_edited_time), { addSuffix: true })}</div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}

export function NotionPageCardSkeleton() {
  return (
    <Card className="w-[300px]">
      <CardContent className="p-3 flex flex-col">
        <div className="flex items-center justify-between gap-2 mb-2">
          <div className="flex items-center gap-2 flex-1 min-w-0">
            <Skeleton className="h-4 w-4 flex-shrink-0" />
            <Skeleton className="h-4 w-3/4" />
          </div>
          <Skeleton className="h-4 w-4 flex-shrink-0" />
        </div>
        <div className="space-y-2">
          <Skeleton className="h-3 w-2/3" />
          <Skeleton className="h-3 w-1/2" />
          <Skeleton className="h-5 w-16 mt-2" />
        </div>
      </CardContent>
    </Card>
  )
}

export function NotionDatabaseList({ databases }: { databases: Database[] }) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Database Name</TableHead>
          <TableHead>Last Updated</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {databases.map((db) => (
          <TableRow key={db.id}>
            <TableCell>{db.title}</TableCell>
            <TableCell>{new Date(db.last_edited_time).toLocaleDateString()}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}

export function NotionDatabaseListSkeleton() {
  return (
    <Card className="w-full max-w-md animate-pulse">
      <CardHeader>
        <Skeleton className="h-4 w-3/4" />
      </CardHeader>
      <CardContent className="space-y-2">
        <Skeleton className="h-4 w-1/2" />
        <Skeleton className="h-4 w-2/3" />
      </CardContent>
    </Card>
  )
}

export function NotionPageListSkeleton() {
  return (
    <div className="container mx-auto p-4">
      <div className="flex flex-wrap gap-4">
        {[1, 2, 3].map((i) => (
          <NotionPageCardSkeleton key={i} />
        ))}
      </div>
    </div>
  )
}

