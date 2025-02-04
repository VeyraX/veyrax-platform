import { format } from "date-fns"
import { MapPin, Calendar, DollarSign } from "lucide-react"
import Image from "next/image"
import Link from "next/link"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import type { Event } from "@/app/modules/agent/components/tools/eventbrite/event-card-types"

function formatDateRange(startDate: Date | string, endDate: Date | string): string {
  const start = startDate instanceof Date ? startDate : new Date(startDate)
  const end = endDate instanceof Date ? endDate : new Date(endDate)

  const startMonth = format(start, "MMM")
  const endMonth = format(end, "MMM")
  const startDay = format(start, "d")
  const endDay = format(end, "d")
  const startTime = format(start, "h:mm a")

  if (startMonth === endMonth) {
    return `${startMonth} ${startDay}-${endDay}, ${startTime}`
  } else {
    return `${startMonth} ${startDay} - ${endMonth} ${endDay}, ${startTime}`
  }
}

export default function EventCard({ event, onSendMessage }: { 
  event: Event
  onSendMessage?: (message: string) => void 
}) {
  const handleSelectTickets = () => {
    if (onSendMessage) {
      onSendMessage(`I'd like to see more details about the event "${event.name}" and book tickets.`);
    }
  };

  return (
    <Card className="w-full max-w-sm overflow-hidden hover:shadow-lg transition-shadow duration-200">
      <div className="relative w-full h-48 bg-muted">
        <img 
          src={event.image || "/placeholder.svg"} 
          alt={event.name} 
          className="absolute inset-0 w-full h-full object-cover"
        />
      </div>
      <CardHeader>
        <CardTitle className="line-clamp-2">{event.name}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        <div className="flex items-center space-x-2 text-sm text-[hsl(var(--eventbrite-blue))]">
          <Calendar className="h-4 w-4 flex-shrink-0" />
          <span>{formatDateRange(event.startDate, event.endDate)}</span>
        </div>
        <div className="flex items-center space-x-2 text-sm text-[hsl(var(--eventbrite-blue))]">
          <MapPin className="h-4 w-4 flex-shrink-0" />
          <span className="line-clamp-1">{event.isOnline ? "Online" : event.location}</span>
        </div>
        <p className="text-sm text-gray-500 line-clamp-2">{event.description}</p>
        <div className="flex items-center space-x-2 text-sm font-semibold text-[hsl(var(--eventbrite-orange))]">
          <DollarSign className="h-4 w-4 flex-shrink-0" />
          <span>{typeof event.price === "number" ? `$${event.price.toFixed(2)}` : "Free"}</span>
        </div>
      </CardContent>
      <CardFooter>
        <Button 
          className="w-full bg-[hsl(var(--eventbrite-orange))] hover:bg-[hsl(var(--eventbrite-orange))] text-white" 
          onClick={handleSelectTickets}
        >
          Select Tickets
        </Button>
      </CardFooter>
    </Card>
  )
}

