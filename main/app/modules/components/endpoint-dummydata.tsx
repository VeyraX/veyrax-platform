import type { EndpointsData } from "./components/endpoint-types"
import { ReactNode } from 'react'
import EventCard from "@/app/modules/agent/components/tools/eventbrite/event-cards/event-card"
import { EventDetailCard } from "@/app/modules/agent/components/tools/eventbrite/event-card-detail/event-card-detail"

export const endpoints = [
  { path: "/get/events/", method: "GET" },
  { path: "/get/event/{id}", method: "GET" },
]

export const endpointsData: EndpointsData = {
  "/get/events/": {
    path: "/get/events/",
    method: "GET",
    description: "Retrieve a paginated list of events from Eventbrite",
    inputSchema: {
      type: "object",
      properties: {
        location: { type: "string", description: "Optional location to filter events" },
      },
    },
    responseSchema: {
      type: "object",
      properties: {
        success: { type: "boolean" },
        events: {
          type: "array",
          items: {
            type: "object",
            properties: {
              id: { type: "string" },
              name: { type: "string" },
              description: { type: "string" },
              startDate: { type: "string", format: "date-time" },
              endDate: { type: "string", format: "date-time" },
              location: { type: "string" },
              isOnline: { type: "boolean" },
              price: { type: "number" },
              image: { type: "string" },
              availableTickets: { type: "number" },
              seats: {
                type: "array",
                items: { type: "string" },
                description: "Optional seat numbers for seated events"
              }
            }
          }
        }
      }
    },
    preview: (
      <div className="flex justify-start">
        <EventCard 
          event={{
            id: "1",
            name: "Tech Conference 2024",
            description: "Join us for the biggest tech conference of the year featuring keynotes from industry leaders, workshops, and networking opportunities.",
            startDate: "2024-06-15T09:00:00Z",
            endDate: "2024-06-17T17:00:00Z",
            location: "San Francisco Convention Center",
            isOnline: false,
            price: 299.99,
            image: "https://images.unsplash.com/photo-1540575467063-178a50c2df87",
            availableTickets: 500,
            seats: [
              { id: "A1", row: "A", seatNumber: 1, isAvailable: true },
              { id: "A2", row: "A", seatNumber: 2, isAvailable: true },
              { id: "B1", row: "B", seatNumber: 1, isAvailable: true },
              { id: "B2", row: "B", seatNumber: 2, isAvailable: true }
            ]
          }}
          onSendMessage={() => {}}
        />
      </div>
    ) as ReactNode,
    code: [
      {
        path: "app/components/eventbrite/event-list.tsx",
        snippet: `
import { Event } from '@/app/models/eventbrite'

export function EventList({ events }: { events: Event[] }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {events.map((event) => (
        <EventCard key={event.id} event={event} />
      ))}
    </div>
  )
}`
      },
      {
        path: "app/models/eventbrite.ts",
        snippet: `
export interface Event {
  id: string
  name: string
  description: string
  startDate: string
  endDate: string
  location: string
  isOnline: boolean
  price: number
  image: string
  availableTickets: number
  seats?: Array<{
    id: string
    row: string
    seatNumber: number
    isAvailable: boolean
  }>
}

export interface EventbriteAPIResponse {
  events: Event[]
  pagination: {
    page_count: number
    page_number: number
    page_size: number
    total_count: number
  }
}`
      },
      {
        path: "app/api/eventbrite/events/route.ts",
        snippet: `
import { NextResponse } from 'next/server'

const EVENTBRITE_API_KEY = process.env.EVENTBRITE_API_KEY
const EVENTBRITE_API_URL = 'https://www.eventbriteapi.com/v3'

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url)
    const location = searchParams.get('location')

    const response = await fetch(\`\${EVENTBRITE_API_URL}/events/search?\${location ? \`location.address=\${location}&\` : ''}\`, {
      headers: {
        'Authorization': \`Bearer \${EVENTBRITE_API_KEY}\`,
      },
    })

    const data = await response.json()
    return NextResponse.json({ success: true, events: data.events })
  } catch (error) {
    return NextResponse.json(
      { success: false, error: 'Failed to fetch events' },
      { status: 500 }
    )
  }
}`
      },
      {
        path: ".env.local",
        snippet: `
EVENTBRITE_API_KEY=your_eventbrite_api_key_here
EVENTBRITE_ORGANIZATION_ID=your_organization_id_here`
      }
    ],
  },

  "/get/event/{id}": {
    path: "/get/event/{id}",
    method: "GET",
    description: "Get detailed information about a specific event",
    inputSchema: {
      type: "object",
      properties: {
        eventId: { type: "string", description: "The ID of the event to fetch" }
      },
      required: ["eventId"]
    },
    responseSchema: {
      type: "object",
      properties: {
        success: { type: "boolean" },
        event: {
          type: "object",
          properties: {
            id: { type: "string" },
            name: { type: "string" },
            description: { type: "string" },
            startDate: { type: "string", format: "date-time" },
            endDate: { type: "string", format: "date-time" },
            location: { type: "string" },
            isOnline: { type: "boolean" },
            price: { type: "number" },
            image: { type: "string" },
            availableTickets: { type: "number" },
            seats: { type: "array", items: { type: "string" } }
          }
        }
      }
    },
    preview: (
      <div className="flex justify-start">
        <EventDetailCard
          event={{
            id: "1",
            name: "Tech Conference 2024",
            description: "Join us for the biggest tech conference of the year featuring keynotes from industry leaders, workshops, and networking opportunities.",
            startDate: "2024-06-15T09:00:00Z",
            endDate: "2024-06-17T17:00:00Z",
            location: "San Francisco Convention Center",
            isOnline: false,
            price: 299.99,
            image: "https://images.unsplash.com/photo-1540575467063-178a50c2df87",
            availableTickets: 500,
            seats: [
              { id: "A1", row: "A", seatNumber: 1, isAvailable: true },
              { id: "A2", row: "A", seatNumber: 2, isAvailable: true },
              { id: "A3", row: "A", seatNumber: 3, isAvailable: true },
              { id: "B1", row: "B", seatNumber: 1, isAvailable: true },
              { id: "B2", row: "B", seatNumber: 2, isAvailable: true },
              { id: "B3", row: "B", seatNumber: 3, isAvailable: true }
            ]
          }}
          onSendMessage={() => {}}
        />
      </div>
    ) as ReactNode,
    code: [
      {
        path: "app/components/eventbrite/event-detail.tsx",
        snippet: `
import { Event } from '@/app/models/eventbrite'
import { format } from 'date-fns'

export function EventDetail({ event }: { event: Event }) {
  return (
    <div className="max-w-4xl mx-auto p-6">
      <img src={event.image} alt={event.name} className="w-full h-64 object-cover rounded-lg" />
      <h1 className="text-2xl font-bold mt-4">{event.name}</h1>
      <div className="flex items-center gap-2 mt-2">
        <span>{format(new Date(event.startDate), "PPP")}</span>
        <span>{event.isOnline ? "Online Event" : event.location}</span>
      </div>
      <p className="mt-4">{event.description}</p>
      <div className="mt-4">
        <span className="font-bold">Price:</span>{event.price}
      </div>
      {event.seats && (
        <div className="mt-4">
          <h2 className="text-xl font-bold">Available Seats</h2>
          <div className="grid grid-cols-4 gap-2 mt-2">
            {event.seats.map((seat) => (
              <div key={seat.id} className="p-2 border rounded">
                {seat.row}{seat.seatNumber}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )`
      },
      {
        path: "app/models/eventbrite-detail.ts",
        snippet: `
export interface EventDetail {
  id: string
  name: string
  description: string
  startDate: string
  endDate: string
  location: string
  isOnline: boolean
  price: number
  image: string
  availableTickets: number
  seats?: Array<{
    id: string
    row: string
    seatNumber: number
    isAvailable: boolean
  }>
  // Additional details specific to single event
  organizer: {
    id: string
    name: string
    description: string
    website?: string
  }
  venue: {
    id: string
    name: string
    address: string
    city: string
    country: string
    postalCode: string
    latitude?: number
    longitude?: number
  }
  ticketClasses: Array<{
    id: string
    name: string
    price: number
    quantity: number
    quantityAvailable: number
  }>
}

export interface EventbriteDetailResponse {
  success: boolean
  event?: EventDetail
  error?: string
}`
      },
      {
        path: "app/api/eventbrite/events/[id]/route.ts",
        snippet: `
import { NextResponse } from 'next/server'

const EVENTBRITE_API_KEY = process.env.EVENTBRITE_API_KEY
const EVENTBRITE_API_URL = 'https://www.eventbriteapi.com/v3'

export async function GET(
  request: Request,
  { params }: { params: { id: string } }
) {
  try {
    // First, fetch the event details
    const eventResponse = await fetch(
      \`\${EVENTBRITE_API_URL}/events/\${params.id}/\`,
      {
        headers: {
          'Authorization': \`Bearer \${EVENTBRITE_API_KEY}\`,
        },
      }
    )

    if (!eventResponse.ok) {
      throw new Error('Failed to fetch event')
    }

    const eventData = await eventResponse.json()

    // Then fetch venue details
    const venueResponse = await fetch(
      \`\${EVENTBRITE_API_URL}/venues/\${eventData.venue_id}/\`,
      {
        headers: {
          'Authorization': \`Bearer \${EVENTBRITE_API_KEY}\`,
        },
      }
    )

    const venueData = await venueResponse.json()

    // Combine and format the response
    const formattedEvent = {
      id: eventData.id,
      name: eventData.name.text,
      description: eventData.description.text,
      startDate: eventData.start.utc,
      endDate: eventData.end.utc,
      location: venueData.address.localized_address_display,
      isOnline: eventData.online_event,
      price: eventData.ticket_classes[0]?.cost?.value || 0,
      image: eventData.logo?.url,
      availableTickets: eventData.ticket_availability.available_count,
      organizer: {
        id: eventData.organizer_id,
        name: eventData.organizer.name,
        description: eventData.organizer.description?.text,
        website: eventData.organizer.website
      },
      venue: {
        id: venueData.id,
        name: venueData.name,
        address: venueData.address.address_1,
        city: venueData.address.city,
        country: venueData.address.country,
        postalCode: venueData.address.postal_code,
        latitude: venueData.latitude,
        longitude: venueData.longitude
      },
      ticketClasses: eventData.ticket_classes.map(ticket => ({
        id: ticket.id,
        name: ticket.name,
        price: ticket.cost?.value || 0,
        quantity: ticket.quantity_total,
        quantityAvailable: ticket.quantity_available
      }))
    }

    return NextResponse.json({ 
      success: true, 
      event: formattedEvent 
    })
  } catch (error) {
    console.error('Error fetching event details:', error)
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to fetch event details' 
      },
      { status: 500 }
    )
  }
}`
      },
      {
        path: ".env.local",
        snippet: `
# Eventbrite API Configuration
EVENTBRITE_API_KEY=your_eventbrite_private_key_here
EVENTBRITE_API_URL=https://www.eventbriteapi.com/v3
EVENTBRITE_ORGANIZATION_ID=your_organization_id_here

# Optional Configuration
EVENTBRITE_WEBHOOK_KEY=your_webhook_key_here
EVENTBRITE_PUBLIC_TOKEN=your_public_token_here
EVENTBRITE_VENUE_ID=your_default_venue_id_here`
      }
    ],
  },
}