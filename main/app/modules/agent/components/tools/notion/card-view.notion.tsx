import type React from "react"
import type { Page, Database, DatabaseWithProperties } from "./types.notion"
import { ToolCard, ToolCardSkeleton } from "../common/tool-card"
import { Table, TableHeader, TableBody, TableCell, TableRow, TableHead } from "@/components/ui/table"
import { Card, CardHeader, CardContent } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { formatDistanceToNow } from "date-fns"

export function NotionPageCard({ title, last_edited_time, url, id }: Page) {
  return (
    <ToolCard
      resourceType="notion/page"
      title={title || "Untitled"}
      subtitle={last_edited_time ? 
        `Edited ${formatDistanceToNow(new Date(last_edited_time), { addSuffix: true })}` : 
        "Just created"
      }
      externalLink={url}
    />
  )
}

export function NotionDatabaseList({ databases }: { databases: Database[] }) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Database Name</TableHead>
          <TableHead>ID</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {databases.map((db) => (
          <TableRow key={db.id}>
            <TableCell>{db.title}</TableCell>
            <TableCell className="font-mono text-sm">{db.id}</TableCell>
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

export function NotionPageCardSkeleton() {
  return <ToolCardSkeleton />
}

export function NotionDatabaseProperties({ database }: { database: DatabaseWithProperties }) {
  return (
    <div className="space-y-4">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Property Name</TableHead>
            <TableHead>Type</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {Object.entries(database.properties).map(([key, property]) => (
            <TableRow key={property.id}>
              <TableCell className="font-medium">{property.name}</TableCell>
              <TableCell>{property.type}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}

