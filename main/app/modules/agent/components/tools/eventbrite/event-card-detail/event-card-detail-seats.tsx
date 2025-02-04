import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import type { Seat } from "@/app/modules/agent/components/tools/eventbrite/event-card-types"

export function SeatSelector({ seats, onSeatSelect }: { 
  seats: Seat[], 
  onSeatSelect: (selectedSeats: string[]) => void 
}) {
  const [selectedSeats, setSelectedSeats] = useState<string[]>([])

  const toggleSeat = (seatId: string) => {
    setSelectedSeats((prev) => (
      prev.includes(seatId) ? prev.filter((s) => s !== seatId) : [...prev, seatId]
    ))
  }

  useEffect(() => {
    onSeatSelect(selectedSeats)
  }, [selectedSeats, onSeatSelect])

  const maxSeatNumber = Math.max(...seats.map(seat => seat.seatNumber))

  return (
    <div className="space-y-4">
      <div className="relative">
        <div className="w-full h-4 bg-gray-300 rounded-t-lg mb-2 flex items-center justify-center text-xs text-gray-600">
          Stage
        </div>
        <div className="grid gap-2" style={{ gridTemplateColumns: `repeat(${maxSeatNumber}, minmax(0, 1fr))` }}>
          {seats.map((seat) => {
            const seatId = `${seat.row}${seat.seatNumber}`
            return (
              <Button
                key={seatId}
                variant={selectedSeats.includes(seatId) ? "default" : "outline"}
                className="w-8 h-8 p-0 text-xs"
                onClick={() => toggleSeat(seatId)}
                disabled={!seat.isAvailable}
              >
                {seatId}
              </Button>
            )
          })}
        </div>
      </div>
      <p className="text-sm text-muted-foreground">
        Selected: {selectedSeats.length} {selectedSeats.length === 1 ? "seat" : "seats"}
      </p>
    </div>
  )
}

