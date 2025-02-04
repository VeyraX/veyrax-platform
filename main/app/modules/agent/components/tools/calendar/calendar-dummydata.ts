"use client"

import { CalendarData } from "./calendar-types"

export const dummyEvents: CalendarData[] = [
  {
    day: new Date("2025-02-03"),
    events: [
      {
        id: 1,
        name: "Q1 Planning Session",
        time: "10:00 AM",
        datetime: "2025-02-03T00:00",
        is_new: false
      },
      {
        id: 2,
        name: "Team Sync",
        time: "2:00 PM",
        datetime: "2025-02-03T00:00",
        is_new: false
      },
    ],
  },
  {
    day: new Date("2025-02-07"),
    events: [
      {
        id: 3,
        name: "Product Launch Review",
        time: "2:00 PM",
        datetime: "2025-02-07T00:00",
        is_new: false
      },
      {
        id: 4,
        name: "Marketing Sync",
        time: "11:00 AM",
        datetime: "2025-02-07T00:00",
        is_new: false
      },
      {
        id: 5,
        name: "Vendor Meeting",
        time: "4:30 PM",
        datetime: "2025-02-07T00:00",
        is_new: false
      },
    ],
  },
  {
    day: new Date("2025-02-10"),
    events: [
      {
        id: 6,
        name: "Team Building Workshop",
        time: "11:00 AM",
        datetime: "2025-02-10T00:00",
        is_new: false
      },
    ],
  },
  {
    day: new Date("2025-02-13"),
    events: [
      {
        id: 7,
        name: "Budget Analysis Meeting",
        time: "3:30 PM",
        datetime: "2025-02-13T00:00",
        is_new: false
      },
      {
        id: 8,
        name: "Sprint Planning",
        time: "9:00 AM",
        datetime: "2025-02-13T00:00",
        is_new: false
      },
      {
        id: 9,
        name: "Design Review",
        time: "1:00 PM",
        datetime: "2025-02-13T00:00",
        is_new: false
      },
    ],
  },
  {
    day: new Date("2025-02-16"),
    events: [
      {
        id: 10,
        name: "Client Presentation",
        time: "10:00 AM",
        datetime: "2025-02-16T00:00",
        is_new: false
      },
      {
        id: 11,
        name: "Team Lunch",
        time: "12:30 PM",
        datetime: "2025-02-16T00:00",
        is_new: false
      },
      {
        id: 12,
        name: "Project Status Update",
        time: "2:00 PM",
        datetime: "2025-02-16T00:00",
        is_new: false
      },
    ],
  },
]