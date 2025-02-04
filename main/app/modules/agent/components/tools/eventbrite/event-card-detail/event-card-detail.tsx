import { useState } from "react"
import { format } from "date-fns"
import { CalendarIcon, MapPinIcon, GlobeIcon, TicketIcon } from "lucide-react"
import type { Event } from "@/app/modules/agent/components/tools/eventbrite/event-card-types"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { SeatSelector } from "./event-card-detail-seats"

interface EventDetailCardProps {
  event?: Event
  isLoading?: boolean
  onSendMessage?: (message: string) => void
}

export function EventDetailCard({ event, isLoading, onSendMessage }: EventDetailCardProps) {
  const [selectedSeats, setSelectedSeats] = useState<string[]>([])

  const handleSeatSelect = (seats: string[]) => {
    setSelectedSeats(seats)
  }

  const handleBooking = () => {
    if (onSendMessage && event) {
      const seatsInfo = selectedSeats.length > 0 
        ? `with selected seats: ${selectedSeats.join(", ")}`
        : `for ${selectedSeats.length} tickets`;
        
      const message = `I would like to book tickets for "${event.name}" ${seatsInfo}. The total price would be $${(Number(event.price) * selectedSeats.length).toFixed(2)}. Please proceed with the booking.`;
      
      onSendMessage(message);
    }
  }

  if (isLoading) {
    return (
      <Card className="w-full max-w-3xl mx-auto">
        <CardHeader>
          <Skeleton className="h-8 w-3/4 mb-2" />
          <div className="flex items-center space-x-2">
            <Skeleton className="h-4 w-1/2" />
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <Skeleton className="w-full h-64 rounded-md" />
          <Skeleton className="h-20 w-full" />
          <div className="flex items-center space-x-2">
            <Skeleton className="h-4 w-1/3" />
          </div>
          <div className="flex items-center space-x-2">
            <Skeleton className="h-4 w-1/4" />
          </div>
          <Skeleton className="h-6 w-20" />
        </CardContent>
        <CardFooter>
          <Skeleton className="h-10 w-full" />
        </CardFooter>
      </Card>
    )
  }

  if (!event) {
    return null
  }

  return (
    <Card className="w-full max-w-3xl mx-auto">
      <div className="flex justify-center py-4 border-b">
        <img 
          src="/logos/eventbrite-icon.svg" 
          alt="Eventbrite Logo" 
          className="h-4"
        />
      </div>
      <CardHeader>
        <CardTitle className="text-2xl font-bold">{event.name}</CardTitle>
        <div className="flex items-center space-x-2 text-sm text-muted-foreground">
          <CalendarIcon className="w-4 h-4" />
          <span>
            {format(event.startDate, "PPP")} - {format(event.endDate, "PPP")}
          </span>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <img src={event.image || "/placeholder.svg"} alt={event.name} className="w-full h-64 object-cover rounded-md" />
        <p className="text-muted-foreground">{event.description}</p>
        <div className="flex items-center space-x-2">
          {event.isOnline ? (
            <>
              <GlobeIcon className="w-4 h-4" />
              <span>Online Event</span>
            </>
          ) : (
            <>
              <MapPinIcon className="w-4 h-4" />
              <span>{event.location}</span>
            </>
          )}
        </div>
        <div className="flex items-center space-x-2">
          <TicketIcon className="w-4 h-4" />
          <span>{event.availableTickets} tickets available</span>
        </div>
        <Badge variant={event.price === 0 || event.price === "Free" ? "secondary" : "default"}
          className={event.price === 0 || event.price === "Free" ? 
            "bg-[hsl(var(--eventbrite-green))] text-white" : 
            "bg-[hsl(var(--eventbrite-orange))] text-white"}
        >
          {event.price === 0 || event.price === "Free" ? "Free" : `$${Number(event.price).toFixed(2)}`}
        </Badge>
        {!event.isOnline && event.seats && (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Select Your Seats</h3>
            <SeatSelector seats={event.seats} onSeatSelect={handleSeatSelect} />
          </div>
        )}
      </CardContent>
      <CardFooter className="flex flex-col space-y-4">
        {selectedSeats.length > 0 && (
          <p className="text-sm">
            Selected seats: {selectedSeats.join(", ")}({selectedSeats.length}{" "}
            {selectedSeats.length === 1 ? "ticket" : "tickets"})
          </p>
        )}
        <Button 
          onClick={handleBooking} 
          className="w-full bg-[hsl(var(--eventbrite-orange))] hover:bg-[hsl(var(--eventbrite-orange))]" 
          disabled={!event.isOnline && selectedSeats.length === 0}
        >
          {event.price === 0 || event.price === "Free" ? "Register" : "Book Now"}
        </Button>
      </CardFooter>
    </Card>
  )
}

