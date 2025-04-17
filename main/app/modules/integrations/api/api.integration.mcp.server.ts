import { createClient } from "@/lib/utils/supabase/server";
import { createClient as createServiceClient } from '@supabase/supabase-js';

export const connectMcpRepository = async (options: {
  user_id: string;
  repo_id: string;
  env?: Record<string, string>;
  status?: string;
}) => {
  const { user_id, repo_id, env, status } = options;
  
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
      env,
      status
    }, {
      onConflict: 'user_id,repo_id'
    });
  
  if (error) {
    throw new Error('Failed to connect MCP repository: ' + error.message);
  }
  
  return { success: true };
};

export const getUserApiKey = async (userId: string): Promise<string | null> => {
  try {
    const client = createServiceClient(
      process.env.SUPABASE_URL!,
      process.env.SUPABASE_SERVICE_KEY!
    );
    
    const { data, error } = await client
      .from('users_api_keys')
      .select('api_key')
      .eq('user_id', userId)
      .single();
    
    if (error || !data) {
      console.error('Error getting user API key:', error);
      return null;
    }
    
    return data.api_key;
  } catch (error) {
    console.error('Error getting user API key:', error);
    return null;
  }
};