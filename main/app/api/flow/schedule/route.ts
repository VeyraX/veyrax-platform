import { NextResponse } from 'next/server';
import { Client } from '@upstash/qstash';

const qstash = new Client({
  token: process.env.QSTASH_TOKEN!
});

export async function POST(request: Request) {
  try {
    const { flowId, schedule, apiKey } = await request.json();

    let cronExpression: string;
    if (schedule.type === 'once') {
      const date = new Date(schedule.oneTime!.datetime);
      cronExpression = `${date.getMinutes()} ${date.getHours()} ${date.getDate()} ${date.getMonth() + 1} *`;
      console.log('One-time cron:', cronExpression, 'for date:', date);
    } else {
      const { recurrence } = schedule;
      const [hours, minutes] = recurrence!.time.split(':');
      if (recurrence!.dayOfWeek !== undefined) {
        cronExpression = `${minutes} ${hours} * * ${recurrence!.dayOfWeek}`;
        console.log('Weekly cron:', cronExpression);
      } else if (recurrence!.dayOfMonth !== undefined) {
        cronExpression = `${minutes} ${hours} ${recurrence!.dayOfMonth} * *`;
        console.log('Monthly cron:', cronExpression);
      } else {
        cronExpression = `${minutes} ${hours} * * *`;
        console.log('Daily cron:', cronExpression);
      }
    }

    const destination = process.env.FRONTEND_URL;
    console.log('Creating QStash schedule:', {
      cron: cronExpression,
      destination: `${destination}/api/flow/qstash`,
      body: { flowId, apiKey }
    });
    
    const qstashSchedule = await qstash.schedules.create({
      cron: cronExpression,
      destination: `${destination}/api/flow/qstash`,
      body: JSON.stringify({
        flowId,
        apiKey
      })
    });

    return NextResponse.json({ scheduleId: qstashSchedule.scheduleId });
  } catch (error) {
    console.error('Error in schedule API:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}

export async function DELETE(request: Request) {
  try {
    const { scheduleId } = await request.json();
    await qstash.schedules.delete(scheduleId);
    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Error deleting schedule:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
} 