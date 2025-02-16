export interface Filters {
    keywords?: string
    attendees?: string
    afterDate?: string
    beforeDate?: string
    calendarId?: string
}

export interface Event {
    id: string
    summary: string
    description?: string
    start: string
    end: string
    htmlLink?: string
    location?: string
    creator?: Record<string, any>
    attendees?: { email: string; displayName?: string }[]
    status?: string
    filters?: Filters
}