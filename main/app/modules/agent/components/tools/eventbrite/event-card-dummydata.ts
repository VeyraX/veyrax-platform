import { Event } from "./event-card-types"

export const dummyEvents: Event[] = [
  {
    id: "1",
    name: "Tech Conference 2025",
    description: "Join us for the biggest tech conference of the year featuring keynotes from industry leaders, workshops, and networking opportunities.",
    startDate: new Date("2025-01-15T09:00:00"),
    endDate: new Date("2025-01-17T17:00:00"),
    location: "San Francisco Convention Center, San Francisco, CA",
    price: 299.99,
    image: "https://images.unsplash.com/photo-1540575467063-178a50c2df87",
    isOnline: false,
    availableTickets: 500,
    seats: [
      { id: "A1", row: "A", seatNumber: 1, isAvailable: true },
      { id: "A2", row: "A", seatNumber: 2, isAvailable: true },
      { id: "A3", row: "A", seatNumber: 3, isAvailable: true },
      { id: "B1", row: "B", seatNumber: 1, isAvailable: true },
      { id: "B2", row: "B", seatNumber: 2, isAvailable: true },
      { id: "B3", row: "B", seatNumber: 3, isAvailable: true },
      { id: "C1", row: "C", seatNumber: 1, isAvailable: true },
      { id: "C2", row: "C", seatNumber: 2, isAvailable: true },
      { id: "C3", row: "C", seatNumber: 3, isAvailable: true }
    ]
  },
  {
    id: "2",
    name: "Virtual Yoga Workshop",
    description: "Transform your practice with our online yoga workshop suitable for all levels. Learn new techniques and deepen your understanding.",
    startDate: new Date("2025-01-20T10:00:00"),
    endDate: new Date("2025-01-20T12:00:00"),
    location: "Online Event",
    price: 25.00,
    image: "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b",
    isOnline: true,
    availableTickets: 100
  },
  {
    id: "3",
    name: "Food & Wine Festival",
    description: "Experience culinary excellence with tastings from top chefs, wine pairings, and live cooking demonstrations.",
    startDate: new Date("2025-01-28T11:00:00"),
    endDate: new Date("2025-01-30T22:00:00"),
    location: "Central Park, New York, NY",
    price: 150.00,
    image: "https://images.unsplash.com/photo-1555939594-58d7cb561ad1",
    isOnline: false,
    availableTickets: 1000,
    seats: [
      { id: "T1", row: "T", seatNumber: 1, isAvailable: true },
      { id: "T2", row: "T", seatNumber: 2, isAvailable: true },
      { id: "T3", row: "T", seatNumber: 3, isAvailable: true },
      { id: "T4", row: "T", seatNumber: 4, isAvailable: true },
      { id: "T5", row: "T", seatNumber: 5, isAvailable: true },
    ]
  },
  {
    id: "4",
    name: "Digital Marketing Masterclass",
    description: "Learn the latest digital marketing strategies from industry experts in this comprehensive online masterclass.",
    startDate: new Date("2025-02-01T14:00:00"),
    endDate: new Date("2025-02-01T17:00:00"),
    location: "Online Event",
    price: 0,
    image: "https://images.unsplash.com/photo-1557804506-669a67965ba0",
    isOnline: true,
    availableTickets: 200
  },
  {
    id: "5",
    name: "Summer Music Festival",
    description: "Three days of non-stop music featuring top artists across multiple genres. Food vendors and camping available.",
    startDate: new Date("2025-02-15T12:00:00"),
    endDate: new Date("2025-02-17T23:00:00"),
    location: "Golden Gate Park, San Francisco, CA",
    price: 199.99,
    image: "https://images.unsplash.com/photo-1459749411175-04bf5292ceea",
    isOnline: false,
    availableTickets: 5000,
    seats: [
      { id: "GA1", row: "GA", seatNumber: 1, isAvailable: true },
      { id: "GA2", row: "GA", seatNumber: 2, isAvailable: true },
      { id: "VIP1", row: "VIP", seatNumber: 1, isAvailable: true },
      { id: "VIP2", row: "VIP", seatNumber: 2, isAvailable: true },
      { id: "VIP3", row: "VIP", seatNumber: 3, isAvailable: true }
    ]
  },
  {
    id: "6",
    name: "Photography Workshop",
    description: "Master the art of photography with hands-on training covering composition, lighting, and post-processing techniques.",
    startDate: new Date("2025-02-25T09:30:00"),
    endDate: new Date("2025-02-25T16:30:00"),
    location: "Seattle Art Museum, Seattle, WA",
    price: 75.00,
    image: "https://images.unsplash.com/photo-1542038784456-1ea8e935640e",
    isOnline: false,
    availableTickets: 30,
    seats: [
      { id: "P1", row: "P", seatNumber: 1, isAvailable: true },
      { id: "P2", row: "P", seatNumber: 2, isAvailable: true },
      { id: "P3", row: "P", seatNumber: 3, isAvailable: true },
      { id: "P4", row: "P", seatNumber: 4, isAvailable: true },
      { id: "P5", row: "P", seatNumber: 5, isAvailable: true }
    ]
  }
]