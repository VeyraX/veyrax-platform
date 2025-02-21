import { createClient } from '@/lib/utils/supabase/client';
import { tools as allTools } from '@/lib/ai/tools';
import { useQuery } from '@tanstack/react-query';


export async function getUserToolsClient() {
  const supabase = createClient();
  
  const { data: { user }, error: userError } = await supabase.auth.getUser();
  if (userError || !user) {
    console.error('Error getting user:', userError);
    return {};
  }

  const { data: availableTools, error } = await supabase
    .rpc('get_user_tools_secure', { user_id_param: user.id })
    .select();

  console.log(availableTools);

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

export const useGetUserTools = () => {
  return useQuery({
    queryKey: ['user-tools'],
    queryFn: getUserToolsClient
  })
}
