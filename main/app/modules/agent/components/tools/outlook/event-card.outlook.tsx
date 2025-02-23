import { EventProps, Filters } from "./types.outlook"
import { SearchIcon } from "lucide-react"
import { ToolCard, ToolCardSkeleton } from "../common/tool-card"

export function EventCard({ subject, start, end, web_link, organizer }: EventProps) {
  const startDate = start ? new Date(start.dateTime) : new Date();
  const endDate = end ? new Date(end.dateTime) : new Date();

  const formatTime = (date: Date) => {
    if (!date || date.toString() === 'Invalid Date') {
      return 'TBD';
    }
    return date.toLocaleTimeString("en-US", {
      hour: "numeric",
      minute: "2-digit",
      hour12: true,
      timeZone: start?.timeZone || 'UTC'
    }).replace(/\s/g, '');
  }

  const organizerName = organizer?.emailAddress?.name || organizer?.emailAddress?.address || 'Unknown';

  return (
    <ToolCard
      resourceType="outlook/event"
      title={subject}
      subtitle={`${formatTime(startDate)} - ${formatTime(endDate)} • ${organizerName}`}
      externalLink={web_link}
    />
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
          {filters.search && ` ${filters.search}`}
          {filters.calendarId && ` Calendar: ${filters.calendarId}`}
        </span>
      </div>
    </div>
  );
}

export function EventCardSkeleton() {
  return <ToolCardSkeleton />
}