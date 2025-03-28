import { createClient } from '@supabase/supabase-js';
import { FlowSchedule, UserFlowSchedule } from './types.flows';
import { Client } from '@upstash/qstash';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_KEY!,
  {
    auth: {
      persistSession: false,
      autoRefreshToken: false,
      detectSessionInUrl: false
    }
  }
);

const qstash = new Client({
  token: process.env.QSTASH_TOKEN!,
  baseUrl: process.env.QSTASH_URL
});

export const getFlowSchedule = async (flowId: string): Promise<FlowSchedule | null> => {
  try {
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
    const { data: apiKeyData, error: apiKeyError } = await supabase
      .from('users_api_keys')
      .select('api_key')
      .single();

    if (apiKeyError || !apiKeyData?.api_key) {
      throw new Error('Failed to get API key');
    }

    const { data: existingSchedule, error: checkError } = await supabase
      .from('user_flow_schedules')
      .select('flow_id, run_id')
      .eq('flow_id', flowId)
      .maybeSingle();

    if (checkError) {
      console.error('Error checking existing schedule:', checkError);
      throw checkError;
    }

    if (existingSchedule?.run_id) {
      try {
        await qstash.schedules.delete(existingSchedule.run_id);
      } catch (error) {
        console.error('Error deleting existing QStash schedule:', error);
      }
    }

    let cronExpression: string;
    if (schedule.type === 'once') {
      const date = new Date(schedule.oneTime!.datetime);
      cronExpression = `${date.getMinutes()} ${date.getHours()} ${date.getDate()} ${date.getMonth() + 1} *`;
    } else {
      const { recurrence } = schedule;
      const [hours, minutes] = recurrence!.time.split(':');
      if (recurrence!.dayOfWeek !== undefined) {
        cronExpression = `${minutes} ${hours} * * ${recurrence!.dayOfWeek}`;
      } else if (recurrence!.dayOfMonth !== undefined) {
        cronExpression = `${minutes} ${hours} ${recurrence!.dayOfMonth} * *`;
      } else {
        cronExpression = `${minutes} ${hours} * * *`;
      }
    }

    const qstashSchedule = await qstash.schedules.create({
      cron: cronExpression,
      destination: `${process.env.FRONTEND_URL}/api/flow/qstash`,
      body: JSON.stringify({
        flowId,
        apiKey: apiKeyData.api_key
      })
    });

    if (existingSchedule) {
      const { error: updateError } = await supabase
        .from('user_flow_schedules')
        .update({ 
          schedule,
          run_id: qstashSchedule.scheduleId
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
          run_id: qstashSchedule.scheduleId
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
      .select('run_id')
      .eq('flow_id', flowId)
      .single();

    if (checkError) {
      if (checkError.code === 'PGRST116') {
        // Schedule doesn't exist, nothing to delete
        return;
      }
      throw checkError;
    }

    // Delete QStash schedule if it exists
    if (existingSchedule?.run_id) {
      try {
        await qstash.schedules.delete(existingSchedule.run_id);
      } catch (error) {
        console.error('Error deleting QStash schedule:', error);
      }
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
    const { data, error } = await supabase
      .from('user_flow_schedules')
      .select(`
        flow_id,
        schedule,
        user_flows!inner (
          user_id
        )
      `);
    
    if (error) throw error;
    
    return data?.map((item: { flow_id: string; schedule: FlowSchedule }) => ({
      flow_id: item.flow_id,
      schedule: item.schedule
    })) || [];
  } catch (error) {
    console.error('Error fetching all flow schedules:', error);
    throw error;
  }
};