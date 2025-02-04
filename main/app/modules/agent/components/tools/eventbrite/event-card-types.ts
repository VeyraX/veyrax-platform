export type Event = {
    id: string
    name: string
    startDate: Date | string
    endDate: Date | string
    description: string
    location: string
    isOnline: boolean
    price: number | "Free"
    availableTickets: number
    image: string
    seats?: Seat[]
  }
  
  

export type Seat = {
  id: string
  row: string
  seatNumber: number
  isAvailable: boolean
}
