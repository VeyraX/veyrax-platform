import { FlowSchedule, UserFlowRun } from "../../api/types.flows";
import { format, parseISO } from "date-fns";
import { useState } from "react";
import { ScheduleSheet } from "./schedule-sheet";

interface ScheduleViewProps {
  schedule?: FlowSchedule | null;
  flowName: string;
  flowRuns: UserFlowRun[];
}

export function ScheduleView({ schedule, flowName, flowRuns }: ScheduleViewProps) {
  const [selectedRun, setSelectedRun] = useState<UserFlowRun | null>(null);

  console.log('ScheduleView received flow runs:', flowRuns);
  
  return (
    <>
      <div className="overflow-x-auto">
        {schedule && (
          <div className="mb-4">
            <ScheduleInfo schedule={schedule} />
          </div>
        )}
        <table className="min-w-full divide-y divide-gray-200 mt-4">
          <thead>
            <tr>
              <th scope="col" className="px-6 py-3 text-left text-sm font-medium">
                Name
              </th>
              <th scope="col" className="px-6 py-3 text-left text-sm font-medium">
                Date
              </th>
              <th scope="col" className="px-6 py-3 text-left text-sm font-medium">
                Status
              </th>
              <th scope="col" className="px-6 py-3 text-left text-sm font-medium">
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {Array.isArray(flowRuns) && flowRuns.length > 0 ? (
              flowRuns.map((run) => (
                <tr key={run.id}>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    {flowName}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {run.run_at ? format(parseISO(run.run_at), 'PPp') : '-'}
                  </td>
                  <td className="px-6 py-4">
                    <StatusBadge status={run.run_status} />
                  </td>
                  <td className="px-6 py-4 text-sm">
                    <button
                      onClick={() => setSelectedRun(run)}
                      className="text-black hover:text-gray-700"
                    >
                      See payload
                    </button>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={4} className="px-6 py-4 text-center text-sm">
                  No flow runs found
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <ScheduleSheet
        isOpen={!!selectedRun}
        onClose={() => setSelectedRun(null)}
        flowRun={selectedRun!}
      />
    </>
  );
}

function StatusBadge({ status }: { status: UserFlowRun['run_status'] }) {
  const statusColors = {
    pending: 'bg-yellow-100 text-yellow-800',
    running: 'bg-blue-100 text-blue-800',
    completed: 'bg-green-100 text-green-800',
    failed: 'bg-red-100 text-red-800',
    started: 'bg-gray-100 text-gray-800',
  };

  return (
    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${statusColors[status]}`}>
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </span>
  );
}

function ScheduleInfo({ schedule }: { schedule: FlowSchedule }) {
  if (schedule.type === 'once' && schedule.oneTime) {
    const datetime = parseISO(schedule.oneTime.datetime);
    return (
      <div className="text-sm text-gray-600">
        Runs once on {format(datetime, 'PPP')} at {format(datetime, 'HH:mm')} UTC
      </div>
    );
  }

  if (schedule.type === 'recurring' && schedule.recurrence) {
    const { dayOfWeek, dayOfMonth, time } = schedule.recurrence;
    const [hours, minutes] = time.split(':');
    const formattedTime = `${hours}:${minutes}`;

    let scheduleText = '';
    if (dayOfWeek !== undefined) {
      const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
      scheduleText = `Every ${days[dayOfWeek]}`;
    } else if (dayOfMonth !== undefined) {
      const suffix = getDaySuffix(dayOfMonth);
      scheduleText = `Every ${dayOfMonth}${suffix} day of the month`;
    } else {
      scheduleText = 'Every day';
    }

    return (
      <div className="text-sm text-gray-600">
        {scheduleText} at {formattedTime} UTC
      </div>
    );
  }

  return null;
}

function getDaySuffix(day: number) {
  if (day > 3 && day < 21) return 'th';
  switch (day % 10) {
    case 1: return "st";
    case 2: return "nd";
    case 3: return "rd";
    default: return "th";
  }
}
