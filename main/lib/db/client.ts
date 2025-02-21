import { createClient } from '@clickhouse/client';

const host = process.env.CLICKHOUSE_HOST;
const protocol = 'https';
const port = process.env.CLICKHOUSE_PORT;

export const clickhouse = createClient({
  url: `${protocol}://${host}:${port}`,
  username: process.env.CLICKHOUSE_USER || 'default',
  password: process.env.CLICKHOUSE_PASSWORD || '',
});

export async function executeQuery(query: string, params?: Record<string, any>) {
    try {
      const resultSet = await clickhouse.query({
        query,
        format: 'JSONEachRow',
        query_params: params,
      });
  
      const rows = await resultSet.json();
      
      return {
        success: true,
        data: rows,
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }