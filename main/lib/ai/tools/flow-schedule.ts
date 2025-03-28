import { tool } from 'ai';
import { z } from 'zod';
import { createOrUpdateFlowSchedule as apiCreateOrUpdateFlowSchedule, deleteFlowSchedule as apiDeleteFlowSchedule, getFlowSchedule as apiGetFlowSchedule, getAllFlowSchedules as apiGetAllFlowSchedules } from '@/app/modules/flows/api/api.server.schedule.flows';
import { FlowSchedule } from '@/app/modules/flows/api/types.flows';

export const flowScheduleTool = tool({
  description: 'Create or update a schedule for a flow',
  parameters: z.object({
    flowId: z.string().describe('ID of the flow to schedule'),
    schedule: z.object({
      type: z.enum(['recurring', 'once']).describe('Type of schedule: recurring or one-time'),
      recurrence: z.object({
        dayOfWeek: z.enum(['0', '1', '2', '3', '4', '5', '6']).transform(Number).optional().describe('Day of week (0-6, where 0 is Sunday)'),
        dayOfMonth: z.number().min(1).max(31).optional().describe('Day of month (1-31)'),
        time: z.string().describe('Time in 24-hour format (e.g., "14:30")'),
        timezone: z.string().describe('Timezone for the schedule')
      }).optional().describe('Recurrence configuration for recurring schedules'),
      oneTime: z.object({
        datetime: z.string().describe('Date and time for one-time execution'),
        timezone: z.string().describe('Timezone for the schedule')
      }).optional().describe('One-time schedule configuration')
    }).refine(
      (data) => {
        if (data.type === 'recurring' && !data.recurrence) {
          return false;
        }
        if (data.type === 'once' && !data.oneTime) {
          return false;
        }
        return true;
      },
      {
        message: "Must provide 'recurrence' for recurring schedules or 'oneTime' for one-time schedules"
      }
    ).describe('Schedule configuration')
  }),
  execute: async function({ flowId, schedule }) {
    try {
      const transformedSchedule: FlowSchedule = {
        type: schedule.type,
        ...(schedule.recurrence && {
          recurrence: {
            ...schedule.recurrence,
            dayOfWeek: schedule.recurrence.dayOfWeek as 0 | 1 | 2 | 3 | 4 | 5 | 6
          }
        }),
        ...(schedule.oneTime && { oneTime: schedule.oneTime })
      };
      
      await apiCreateOrUpdateFlowSchedule(flowId, transformedSchedule);
      return {
        success: true,
        message: 'Schedule created/updated successfully'
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to create/update flow schedule'
      };
    }
  }
});

export const deleteFlowScheduleTool = tool({
  description: 'Delete a schedule for a specific flow',
  parameters: z.object({
    flowId: z.string().describe('ID of the flow to delete schedule for')
  }),
  execute: async function({ flowId }) {
    try {
      await apiDeleteFlowSchedule(flowId);
      return {
        success: true,
        message: 'Schedule deleted successfully'
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to delete flow schedule'
      };
    }
  }
});