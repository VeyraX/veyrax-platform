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
    name: "Broadway Musical Showcase",
    description: "Experience the magic of Broadway with performances from current hit shows and emerging talents.",
    startDate: new Date("2025-02-05T19:00:00"),
    endDate: new Date("2025-02-05T22:00:00"),
    location: "Times Square Theater, New York, NY",
    price: 125.00,
    image: "https://images.unsplash.com/photo-1507676184212-d03ab07a01bf",
    isOnline: false,
    availableTickets: 300,
    seats: [
      { id: "O1", row: "O", seatNumber: 1, isAvailable: true },
      { id: "O2", row: "O", seatNumber: 2, isAvailable: true },
      { id: "O3", row: "O", seatNumber: 3, isAvailable: true },
      { id: "O4", row: "O", seatNumber: 4, isAvailable: true },
      { id: "O5", row: "O", seatNumber: 5, isAvailable: true }
    ]
  },
  {
    id: "5",
    name: "Art Gallery Exhibition",
    description: "Contemporary art exhibition featuring works from emerging New York artists across various mediums.",
    startDate: new Date("2025-02-10T10:00:00"),
    endDate: new Date("2025-02-12T18:00:00"),
    location: "Metropolitan Museum of Art, New York, NY",
    price: 45.00,
    image: "https://images.unsplash.com/photo-1536924940846-227afb31e2a5",
    isOnline: false,
    availableTickets: 200,
    seats: [
      { id: "E1", row: "E", seatNumber: 1, isAvailable: true },
      { id: "E2", row: "E", seatNumber: 2, isAvailable: true },
      { id: "E3", row: "E", seatNumber: 3, isAvailable: true }
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
  },
  {
    id: "7",
    name: "Valentine's Day Concert",
    description: "A romantic evening of classical music featuring renowned musicians performing love-themed compositions.",
    startDate: new Date("2025-02-14T20:00:00"),
    endDate: new Date("2025-02-14T22:30:00"),
    location: "Carnegie Hall, New York, NY",
    price: 85.00,
    image: "https://images.unsplash.com/photo-1514320291840-2e0a9bf2a9ae",
    isOnline: false,
    availableTickets: 400,
    seats: [
      { id: "V1", row: "V", seatNumber: 1, isAvailable: true },
      { id: "V2", row: "V", seatNumber: 2, isAvailable: true },
      { id: "V3", row: "V", seatNumber: 3, isAvailable: true },
      { id: "V4", row: "V", seatNumber: 4, isAvailable: true }
    ]
  },
  {
    id: "8",
    name: "Winter Film Festival",
    description: "Three-day showcase of independent films from around the world, featuring Q&A sessions with directors.",
    startDate: new Date("2025-02-20T11:00:00"),
    endDate: new Date("2025-02-22T23:00:00"),
    location: "Lincoln Center, New York, NY",
    price: 65.00,
    image: "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba",
    isOnline: false,
    availableTickets: 250,
    seats: [
      { id: "F1", row: "F", seatNumber: 1, isAvailable: true },
      { id: "F2", row: "F", seatNumber: 2, isAvailable: true },
      { id: "F3", row: "F", seatNumber: 3, isAvailable: true },
      { id: "F4", row: "F", seatNumber: 4, isAvailable: true },
      { id: "F5", row: "F", seatNumber: 5, isAvailable: true }
    ]
  }
]