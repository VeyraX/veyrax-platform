import React, { useState, useEffect } from "react";
import { Calendar } from "@/components/ui/calendar";
import { Button } from "@/components/ui/button";
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Clock, Loader2 } from "lucide-react";
import { toast } from "sonner";
import { format, parseISO, formatISO } from "date-fns";
import { createOrUpdateFlowSchedule, deleteFlowSchedule, getFlowSchedule } from "../../api/api.schedule.flows";
import { FlowSchedule } from "../../api/types.flows";

interface ScheduleTabContentProps {
  flowId?: string;
  isLoading?: boolean;
  onScheduleChange: (schedule: FlowSchedule | null) => void;
}

export function ScheduleTabContent({ 
  flowId, 
  isLoading,
  onScheduleChange 
}: ScheduleTabContentProps) {
  const [currentSchedule, setCurrentSchedule] = useState<FlowSchedule | null>(null);
  const [isLoadingSchedule, setIsLoadingSchedule] = useState(false);
  const [isEnabled, setIsEnabled] = useState(false);
  const [date, setDate] = useState<Date>();
  const [hour, setHour] = useState("09");
  const [minute, setMinute] = useState("00");
  const [scheduleType, setScheduleType] = useState<'once' | 'daily' | 'weekly' | 'monthly'>('weekly');
  const [recurringDay, setRecurringDay] = useState<number>(4);
  const [monthlyDay, setMonthlyDay] = useState<number>(1);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    const loadSchedule = async () => {
      if (!flowId) return;
      
      try {
        setIsLoadingSchedule(true);
        const schedule = await getFlowSchedule(flowId);
        setCurrentSchedule(schedule);
        setIsEnabled(!!schedule);
        
        if (schedule) {
          if (schedule.type === 'once' && schedule.oneTime) {
            setScheduleType('once');
            const datetime = parseISO(schedule.oneTime.datetime);
            setDate(datetime);
            setHour(format(datetime, 'HH'));
            setMinute(format(datetime, 'mm'));
          } else if (schedule.recurrence) {
            if (schedule.recurrence.dayOfWeek !== undefined) {
              setScheduleType('weekly');
              setRecurringDay(schedule.recurrence.dayOfWeek);
            } else if (schedule.recurrence.dayOfMonth !== undefined) {
              setScheduleType('monthly');
              setMonthlyDay(schedule.recurrence.dayOfMonth);
            } else {
              setScheduleType('daily');
            }
            const [hours, minutes] = schedule.recurrence.time.split(':');
            setHour(hours);
            setMinute(minutes);
          }
        }
      } catch (error) {
        console.error('Error loading schedule:', error);
        toast.error('Failed to load schedule');
      } finally {
        setIsLoadingSchedule(false);
      }
    };

    loadSchedule();
  }, [flowId]);

  const weekDays = [
    { value: 0, label: "Sunday" },
    { value: 1, label: "Monday" },
    { value: 2, label: "Tuesday" },
    { value: 3, label: "Wednesday" },
    { value: 4, label: "Thursday" },
    { value: 5, label: "Friday" },
    { value: 6, label: "Saturday" }
  ];

  const monthDays = Array.from({ length: 31 }, (_, i) => ({
    value: i + 1,
    label: `${i + 1}${getDaySuffix(i + 1)}`
  }));

  function getDaySuffix(day: number) {
    if (day > 3 && day < 21) return 'th';
    switch (day % 10) {
      case 1: return "st";
      case 2: return "nd";
      case 3: return "rd";
      default: return "th";
    }
  }

  const handleScheduleSave = async () => {
    if (!flowId) {
      toast.error("Please save the flow first");
      return;
    }

    try {
      setIsSaving(true);
      
      if (!isEnabled) {
        await deleteFlowSchedule(flowId);
        setCurrentSchedule(null);
        onScheduleChange(null);
        toast.success("Schedule disabled");
        return;
      }

      if (isEnabled) {
        if (!date && scheduleType === 'once') {
          toast.error("Please select a date");
          return;
        }

        const time = `${hour}:${minute}`;
        const schedule: FlowSchedule = {
          type: scheduleType === 'daily' || scheduleType === 'weekly' || scheduleType === 'monthly' ? 'recurring' : 'once',
          ...(scheduleType === 'once' 
            ? {
                oneTime: {
                  datetime: formatISO(new Date(format(date!, 'yyyy-MM-dd') + 'T' + time)),
                  timezone: 'UTC'
                }
              }
            : {
                recurrence: {
                  ...(scheduleType === 'weekly' && { dayOfWeek: recurringDay as 0 | 1 | 2 | 3 | 4 | 5 | 6 }),
                  ...(scheduleType === 'monthly' && { dayOfMonth: monthlyDay }),
                  time: `${time}:00`,
                  timezone: 'UTC'
                }
              }
          )
        };

        await createOrUpdateFlowSchedule(flowId, schedule);
        setCurrentSchedule(schedule);
        onScheduleChange(schedule);
        toast.success("Schedule updated successfully");
      }
    } catch (error) {
      console.error("Error saving schedule:", error);
      toast.error("Failed to update schedule");
    } finally {
      setIsSaving(false);
    }
  };

  const TimeSelector = () => (
    <div className="flex gap-2">
      <Select value={hour} onValueChange={setHour}>
        <SelectTrigger className="w-[100px]">
          <SelectValue placeholder="Hour" />
        </SelectTrigger>
        <SelectContent>
          {Array.from({ length: 24 }).map((_, hour) => (
            <SelectItem 
              key={hour} 
              value={hour.toString().padStart(2, '0')}
            >
              {hour.toString().padStart(2, '0')}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      <span className="text-lg self-center">:</span>
      <Select value={minute} onValueChange={setMinute}>
        <SelectTrigger className="w-[100px]">
          <SelectValue placeholder="Minute" />
        </SelectTrigger>
        <SelectContent>
          {Array.from({ length: 60 }).map((_, minute) => (
            <SelectItem 
              key={minute} 
              value={minute.toString().padStart(2, '0')}
            >
              {minute.toString().padStart(2, '0')}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );

  return (
    <div className="flex flex-col h-full">
      <div className="flex-grow space-y-4 p-4">
        <div className="flex items-center justify-between space-x-2">
          <div className="space-y-0.5">
            <h3 className="text-sm font-medium">Enable Scheduling</h3>
            <p className="text-xs text-gray-500">
              Turn on to schedule automatic runs of this flow
            </p>
          </div>
          <Switch
            checked={isEnabled}
            onCheckedChange={(checked: boolean) => {
              setIsEnabled(checked);
            }}
          />
        </div>

        {isEnabled && (
          <>
            <Select
              value={scheduleType}
              onValueChange={(value: 'once' | 'daily' | 'weekly' | 'monthly') => setScheduleType(value)}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select schedule type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="once">One-time</SelectItem>
                <SelectItem value="daily">Daily</SelectItem>
                <SelectItem value="weekly">Weekly</SelectItem>
                <SelectItem value="monthly">Monthly</SelectItem>
              </SelectContent>
            </Select>

            {scheduleType === 'once' && (
              <>
                <div className="flex justify-center">
                  <Calendar
                    mode="single"
                    selected={date}
                    onSelect={setDate}
                    className="rounded-md border"
                  />
                </div>
                <TimeSelector />
              </>
            )}

            {scheduleType === 'weekly' && (
              <>
                <Select
                  value={recurringDay.toString()}
                  onValueChange={(value) => setRecurringDay(parseInt(value))}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select day of week" />
                  </SelectTrigger>
                  <SelectContent>
                    {weekDays.map((day) => (
                      <SelectItem key={day.value} value={day.value.toString()}>
                        {day.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <TimeSelector />
              </>
            )}

            {scheduleType === 'monthly' && (
              <>
                <Select
                  value={monthlyDay.toString()}
                  onValueChange={(value) => setMonthlyDay(parseInt(value))}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select day of month" />
                  </SelectTrigger>
                  <SelectContent>
                    {monthDays.map((day) => (
                      <SelectItem key={day.value} value={day.value.toString()}>
                        {day.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <TimeSelector />
              </>
            )}

            {scheduleType === 'daily' && (
              <TimeSelector />
            )}
          </>
        )}
      </div>

      <div className="w-full bg-background pt-2 px-6 mt-auto">
        <div className="flex gap-3 mt-2">
          <Button 
            onClick={handleScheduleSave} 
            className="flex-1" 
            disabled={isSaving || !flowId}
          >
            {isSaving ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              "Save"
            )}
          </Button>
        </div>
      </div>
    </div>
  );
} 