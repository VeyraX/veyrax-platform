import { createClient } from "@/lib/utils/supabase/server";
import { createClient as createServiceClient } from '@supabase/supabase-js';

export const connectMcpRepository = async (options: {
  user_id: string;
  repo_id: string;
  env?: Record<string, string>;
}) => {
  const { user_id, repo_id, env } = options;
  
  let client;
  
  if (user_id) {
    client = createServiceClient(
      process.env.SUPABASE_URL!,
      process.env.SUPABASE_SERVICE_KEY!
    );
  } else {
    client = createClient();
    const { data: { user } } = await client.auth.getUser();
    if (!user?.id) {
      throw new Error('Unauthorized - User ID not found');
    }
  }
  
  const { error } = await client
    .from('users_mcp')
    .upsert({
      user_id,
      repo_id,
      env
    }, {
      onConflict: 'user_id,repo_id'
    });
  
  if (error) {
    throw new Error('Failed to connect MCP repository: ' + error.message);
  }
  
  return { success: true };
};
