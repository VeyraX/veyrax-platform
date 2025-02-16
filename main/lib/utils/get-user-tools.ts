import { createClient } from '@/lib/utils/supabase/server';
import { tools as allTools } from '@/lib/ai/tools';

export async function getUserTools(userId: string) {
  const supabase = createClient();
  
  const { data: availableTools, error } = await supabase
    .rpc('get_user_tools_secure', { user_id_param: userId })
    .select();

  if (error) {
    console.error('Error fetching user tools:', error);
    return {};
  }

  if (!availableTools) {
    return {};
  }

  return Object.fromEntries(
    availableTools
      .filter(tool => tool.tool_name in allTools)
      .map(tool => [tool.tool_name, allTools[tool.tool_name as keyof typeof allTools]])
  );
}