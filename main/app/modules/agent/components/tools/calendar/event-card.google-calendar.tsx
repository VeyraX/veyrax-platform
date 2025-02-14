import { CalendarIcon, ExternalLink } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import { Event, Filters } from "./types.google-calendar"
import { SearchIcon, UsersIcon } from "lucide-react"
import { Skeleton } from "@/components/ui/skeleton"

export function EventCard({ summary, start, end, htmlLink }: Event) {
  const startDate = start ? new Date(start) : new Date();
  const endDate = end ? new Date(end) : new Date();

  const formatTime = (date: Date) => {
    if (!date || date.toString() === 'Invalid Date') {
      return 'TBD';
    }
    return date.toLocaleTimeString("en-US", {
      hour: "numeric",
      minute: "2-digit",
      hour12: true,
      timeZone: 'America/Los_Angeles'
    }).replace(/\s/g, '');
  }

  return (
    <Card className="w-[300px] inline-block mr-3">
      <CardContent className="p-3 flex flex-col">
        <div className="flex items-center justify-between gap-2 mb-2">
          <div className="flex items-center gap-2 flex-1 min-w-0">
            <CalendarIcon className="h-4 w-4 text-muted-foreground flex-shrink-0" />
            <span className="truncate text-sm font-medium">{summary}</span>
          </div>
          {htmlLink && (
            <a
              href={htmlLink}
              target="_blank"
              rel="noopener noreferrer"
              className="text-muted-foreground hover:text-foreground"
            >
              <ExternalLink className="h-4 w-4 flex-shrink-0" />
            </a>
          )}
        </div>
        <div className="text-xs text-muted-foreground">
          {formatTime(startDate)} - {formatTime(endDate)}
        </div>
      </CardContent>
    </Card>
  )
}

interface FilterDisplayProps {
  filters: Filters;
}

export function FilterDisplay({ filters }: FilterDisplayProps) {
  if (!filters || Object.keys(filters).every(key => !filters[key as keyof typeof filters])) {
    return null;
  }

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric'
    });
  };

  return (
    <div className="mb-4">
      <div className="inline-flex items-center gap-2.5 px-4 py-2 rounded-full bg-muted/80">
        <SearchIcon className="h-4 w-4 text-muted-foreground" />
        <span className="text-sm">
          {filters.afterDate && formatDate(filters.afterDate)}
          {filters.afterDate && filters.beforeDate && ' - '}
          {filters.beforeDate && formatDate(filters.beforeDate)}
          {filters.keywords && ` ${filters.keywords}`}
          {filters.attendees && ` ${filters.attendees}`}
        </span>
      </div>
    </div>
  );
}

export function EventCardSkeleton() {
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
  );
}

