export interface Event {
    id: number;
    name: string;
    time: string;
    datetime: string;
    is_new?: boolean
  }
  
  export interface CalendarData {
    day: Date;
    events: Event[];
  }
  
  export interface FullScreenCalendarProps {
    data: CalendarData[];
  }