import { Skeleton } from "@/components/ui/skeleton"
import EventCard from "./event-card"
import type { Event } from "../event-card-types"

interface EventCardsListProps {
  events?: Event[]
  isLoading?: boolean
  onSendMessage?: (message: string) => void
}

export function EventCardsList({ events, isLoading, onSendMessage }: EventCardsListProps) {
  if (isLoading) {
    return (
      <>
        <div className="flex justify-center mb-3">
          <img 
            src="/logos/eventbrite-icon.svg" 
            alt="Eventbrite Logo" 
            className="h-4"
          />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="border rounded-lg p-4">
              <Skeleton className="h-[200px] w-full rounded-lg mb-4" />
              <Skeleton className="h-6 w-3/4 mb-2" />
              <Skeleton className="h-4 w-1/2 mb-2" />
              <Skeleton className="h-4 w-1/3" />
            </div>
          ))}
        </div>
      </>
    )
  }

  if (!events?.length) {
    return null
  }

  return (
    <div className="flex flex-col items-center gap-4">
      <div className="flex justify-center w-full mb-1">
        <img 
          src="/logos/eventbrite-icon.svg" 
          alt="Eventbrite Logo" 
          className="h-4"
        />
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 w-full">
        {events.map((event) => (
          <EventCard 
            key={event.id} 
            event={event}
            onSendMessage={onSendMessage}
          />
        ))}
      </div>
    </div>
  )
}