import { Event, Filters } from "./types.google-calendar"
import { SearchIcon } from "lucide-react"
import { ToolCard, ToolCardSkeleton } from "../common/tool-card"

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
    <ToolCard
      resourceType="google-calendar/event"
      title={summary}
      subtitle={`${formatTime(startDate)} - ${formatTime(endDate)}`}
      externalLink={htmlLink}
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
          {filters.keywords && ` ${filters.keywords}`}
          {filters.attendees && ` ${filters.attendees}`}
        </span>
      </div>
    </div>
  );
}

export function EventCardSkeleton() {
  return <ToolCardSkeleton />
}

