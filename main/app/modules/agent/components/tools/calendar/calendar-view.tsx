"use client"

import { FullScreenCalendar } from "@/components/ui/full-screen-calendar"
import { dummyEvents } from "./calendar-dummydata"
import { CalendarData } from "./calendar-types"
import Image from "next/image"

export function CalendarView({ data }: { data: CalendarData[] }) {

    const initial_data = [...dummyEvents, ...data]
    
    return (
        <div className="flex h-screen flex-1 flex-col border rounded-lg">
            <div className="flex justify-center py-4 border-b">
                <Image 
                    src="/logos/google-calendar-logo.svg" 
                    alt="Google Calendar"
                    width={24}
                    height={24}
                />
            </div>
            <FullScreenCalendar data={initial_data} />
        </div>
    )
}