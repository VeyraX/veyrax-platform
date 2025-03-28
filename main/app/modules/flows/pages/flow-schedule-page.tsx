import { useEffect, useState } from 'react';
import { ScheduleView } from '../components/schedule/schedule-view';
import { FlowSchedule, UserFlow, UserFlowRun } from '../api/types.flows';
import { getFlowSchedule, getFlowRuns } from '../api/api.schedule.flows';
import { useRouter } from 'next/router';

interface FlowSchedulePageProps {
  flowId: string;
  flow: UserFlow;
}

export default function FlowSchedulePage({ flowId, flow }: FlowSchedulePageProps) {
  const [schedule, setSchedule] = useState<FlowSchedule | null>(null);
  const [flowRuns, setFlowRuns] = useState<UserFlowRun[]>([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const [scheduleData, runsData] = await Promise.all([
          getFlowSchedule(flowId),
          getFlowRuns(flowId)
        ]);
        console.log('Loaded schedule:', scheduleData);
        console.log('Loaded flow runs:', runsData);
        setSchedule(scheduleData);
        setFlowRuns(runsData);
      } catch (error) {
        console.error('Error loading data:', error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [flowId]);

  const handleViewDetails = (runId: string) => {
    console.log('Viewing details for run:', runId);
    router.push(`/flows/${flowId}/runs/${runId}`);
  };

  if (loading) {
    return (
      <div className="p-4">
        <div className="text-gray-600">Loading...</div>
      </div>
    );
  }

  console.log('Rendering with flow runs:', flowRuns);

  if (!schedule) {
    return (
      <div className="p-4">
        <div className="text-gray-600">No schedule configured</div>
      </div>
    );
  }

  return (
    <div className="p-4">
      <h1 className="text-2xl font-semibold mb-6">Flow Schedule: {flow.name}</h1>
      <ScheduleView
        schedule={schedule}
        flowName={flow.name}
        flowRuns={flowRuns}
      />
    </div>
  );
}
