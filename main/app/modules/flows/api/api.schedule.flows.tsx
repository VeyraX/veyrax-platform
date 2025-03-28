import { createClient } from '@/lib/utils/supabase/client';
import { FlowSchedule, UserFlowSchedule, UserFlowRun } from './types.flows';
import { Client } from '@upstash/qstash';

const supabase = createClient();

const qstash = new Client({ 
  token: process.env.QSTASH_TOKEN! 
});

export const getFlowSchedule = async (flowId: string): Promise<FlowSchedule | null> => {
  try {
    const { data: { user } } = await supabase.auth.getUser();
    
    if (!user) {
      throw new Error('Not authenticated');
    }
    
    const { data, error } = await supabase
      .from('user_flow_schedules')
      .select('schedule')
      .eq('flow_id', flowId)
      .single();
    
    if (error) {
      if (error.code === 'PGRST116') {
        return null;
      }
      throw error;
    }
    
    return data?.schedule || null;
  } catch (error) {
    console.error('Error fetching flow schedule:', error);
    throw error;
  }
};

export const createOrUpdateFlowSchedule = async (flowId: string, schedule: FlowSchedule): Promise<void> => {
  try {
    const { data: { user } } = await supabase.auth.getUser();
    
    if (!user) {
      throw new Error('Not authenticated');
    }

    const { data: apiKeyData, error: apiKeyError } = await supabase
      .from('users_api_keys')
      .select('api_key')
      .single();

    if (apiKeyError || !apiKeyData?.api_key) {
      throw new Error('Failed to get API key');
    }

    const { data: existingSchedule, error: checkError } = await supabase
      .from('user_flow_schedules')
      .select('id, qstash_schedule_id')
      .eq('flow_id', flowId)
      .maybeSingle();

    const { data: flow, error: flowError } = await supabase
      .from('user_flows')
      .select('status')
      .eq('id', flowId)
      .maybeSingle();

    if (checkError) {
      console.error('Error checking existing schedule:', checkError);
      throw checkError;
    }

    if (existingSchedule?.qstash_schedule_id) {
      try {
        await fetch('/api/flow/schedule', {
          method: 'DELETE',
          body: JSON.stringify({ scheduleId: existingSchedule.qstash_schedule_id })
        });
      } catch (error) {
        console.error('Error deleting existing QStash schedule:', error);
      }
    }

    const response = await fetch('/api/flow/schedule', {
      method: 'POST',
      body: JSON.stringify({
        flowId,
        schedule,
        apiKey: apiKeyData.api_key,
        status: flow?.status
      })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to create schedule');
    }

    const { scheduleId } = await response.json();

    if (existingSchedule) {
      const { error: updateError } = await supabase
        .from('user_flow_schedules')
        .update({ 
          schedule,
          qstash_schedule_id: scheduleId
        })
        .eq('flow_id', flowId);

      if (updateError) {
        console.error('Update error:', updateError);
        throw updateError;
      }
    } else {
      const { error: insertError } = await supabase
        .from('user_flow_schedules')
        .insert({ 
          flow_id: flowId,
          schedule,
          qstash_schedule_id: scheduleId
        });

      if (insertError) {
        console.error('Insert error:', insertError);
        throw insertError;
      }
    }
  } catch (error) {
    console.error('Error creating/updating flow schedule:', error);
    throw error;
  }
};

export const deleteFlowSchedule = async (flowId: string): Promise<void> => {
  try {
    const { data: existingSchedule, error: checkError } = await supabase
      .from('user_flow_schedules')
      .select('id, qstash_schedule_id')
      .eq('flow_id', flowId)
      .single();

    if (checkError) {
      if (checkError.code === 'PGRST116') {
        return;
      }
      throw checkError;
    }

    if (existingSchedule?.qstash_schedule_id) {
      await fetch('/api/flow/schedule', {
        method: 'DELETE',
        body: JSON.stringify({ scheduleId: existingSchedule.qstash_schedule_id })
      });
    }

    const { error } = await supabase
      .from('user_flow_schedules')
      .delete()
      .eq('flow_id', flowId);
    
    if (error) throw error;
  } catch (error) {
    console.error('Error deleting flow schedule:', error);
    throw error;
  }
};

export const getAllFlowSchedules = async (): Promise<UserFlowSchedule[]> => {
  try {
    const { data: { user } } = await supabase.auth.getUser();
    
    if (!user) {
      throw new Error('Not authenticated');
    }
    
    const { data, error } = await supabase
      .from('user_flow_schedules')
      .select(`
        flow_id,
        schedule,
        user_flows!inner (
          user_id
        )
      `)
      .eq('user_flows.user_id', user.id);
    
    if (error) throw error;
    
    return data?.map(item => ({
      flow_id: item.flow_id,
      schedule: item.schedule
    })) || [];
  } catch (error) {
    console.error('Error fetching all flow schedules:', error);
    throw error;
  }
};

export const validateSchedule = (schedule: FlowSchedule): boolean => {
  try {
    if (schedule.type !== 'once' && schedule.type !== 'recurring') {
      return false;
    }

    if (schedule.type === 'once') {
      if (!schedule.oneTime?.datetime || !schedule.oneTime?.timezone) {
        return false;
      }
    } else {
      if (!schedule.recurrence?.time || !schedule.recurrence?.timezone) {
        return false;
      }

      if (schedule.recurrence.dayOfWeek !== undefined) {
        if (![0, 1, 2, 3, 4, 5, 6].includes(schedule.recurrence.dayOfWeek)) {
          return false;
        }
      }
    }

    return true;
  } catch (error) {
    return false;
  }
};

export const getFlowRuns = async (flowId: string): Promise<UserFlowRun[]> => {
  try {
    const { data: { user } } = await supabase.auth.getUser();
    
    if (!user) {
      throw new Error('Not authenticated');
    }
    
    const { data, error } = await supabase
      .from('user_flow_runs')
      .select('id, flow_id, run_status, run_at, completed_at, payload')
      .eq('flow_id', flowId)
      .order('run_at', { ascending: false });
    
    if (error) {
      console.error('Error fetching flow runs:', error);
      throw error;
    }
    
    return data || [ ];
  } catch (error) {
    console.error('Error in getFlowRuns:', error);
    throw error;
  }
};
