import { Terminal, Star, Calendar, Award } from "lucide-react";
import { Tool, McpDetails } from "@/app/modules/integrations/api/types.integrations.mcp";
import { useState, useMemo } from "react";
import { Button } from "@/components/ui/button";
import Image from "next/image";
import { GitHubRepoInfo } from "@/app/modules/integrations/api/api.integrations.mcp";
import { formatDistanceToNow } from "date-fns";

interface McpOverviewProps {
  imageName: string;
  mcpDetails: McpDetails | null;
  tools: Tool[];
  mcpId: string;
  repoName: string;
  githubUrl: string;
  deploymentStatus: 'Active' | 'Inactive';
  dummyMetrics: {
    monthlyToolCalls: string;
    license: string;
    local: string;
    published: string;
  };
  repoInfo: GitHubRepoInfo | null;
}

export function McpOverview({
  imageName,
  mcpDetails,
  tools,
  mcpId,
  repoName,
  githubUrl,
  deploymentStatus,
  dummyMetrics,
  repoInfo
}: McpOverviewProps) {
  const [showAllTools, setShowAllTools] = useState(false);
  
  const visibleTools = showAllTools ? tools : tools.slice(0, 4);
  const hasMoreTools = tools.length > 4;
  
  const { owner, repo } = useMemo(() => {
    try {
      if (!githubUrl) return { owner: "", repo: "" };
      
      const normalizedUrl = githubUrl.endsWith('/') 
        ? githubUrl.slice(0, -1) 
        : githubUrl;
      
      const parts = normalizedUrl.split('/');
      const repo = parts[parts.length - 1];
      const owner = parts[parts.length - 2];
      
      return { owner, repo };
    } catch (error) {
      console.error("Error parsing GitHub URL:", error);
      return { owner: "", repo: "" };
    }
  }, [githubUrl]);

  const formattedCreatedAt = useMemo(() => {
    if (!repoInfo?.created_at) return null;
    try {
      return formatDistanceToNow(new Date(repoInfo.created_at), { addSuffix: true });
    } catch (error) {
      return null;
    }
  }, [repoInfo?.created_at]);
  
  return (
    <div className="space-y-6">
      <div className="bg-white dark:bg-gray-900 rounded-md border border-gray-200 dark:border-gray-800 p-6 space-y-4">
        <div className="flex flex-col">
          <h2 className="text-xl font-medium text-foreground">{repoName}</h2>
          <div className="flex items-center gap-2 mt-1">
            <a href={githubUrl} target="_blank" rel="noopener noreferrer" 
              className="flex items-center gap-2 hover:text-blue-600 dark:hover:text-blue-400">
              <Image
                src="https://zpjxdtvecaxrdxvfaxom.supabase.co/storage/v1/object/public/logos//github-logo.svg"
                alt="GitHub"
                width={14}
                height={14}
              />
              <span className="text-sm text-muted-foreground">
                {owner && repo ? `${owner}/${repo}` : imageName}
              </span>
            </a>
          </div>
        </div>
        
        {/* GitHub Stats - Minimal cards */}
        <div className="flex flex-wrap gap-2 mb-4">
          <div className="inline-flex items-center gap-1 bg-gray-100 dark:bg-gray-800 rounded-md px-2 py-1 text-xs">
            <Star size={12} className="text-yellow-500" />
            <span>{repoInfo?.stars || '0'} stars</span>
          </div>
          
          <div className="inline-flex items-center gap-1 bg-gray-100 dark:bg-gray-800 rounded-md px-2 py-1 text-xs">
            <Calendar size={12} className="text-blue-500" />
            <span>Published {formattedCreatedAt || dummyMetrics.published}</span>
          </div>
          
          <div className="inline-flex items-center gap-1 bg-gray-100 dark:bg-gray-800 rounded-md px-2 py-1 text-xs">
            <Award size={12} className="text-green-500" />
            <span>{repoInfo?.license?.name || dummyMetrics.license}</span>
          </div>
        </div>
        
        <div className="text-foreground/90">
          <p>{mcpDetails?.description || "No description available"}</p>
        </div>
      </div>
      
      {/* Tools Panel */}
      <div className="bg-white dark:bg-gray-900 rounded-md border border-gray-200 dark:border-gray-800 p-6 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Terminal size={16} className="text-muted-foreground" />
            <h2 className="text-xl font-medium text-foreground">Tools</h2>
          </div>
          {tools.length > 0 && (
            <div className="text-xs text-muted-foreground">
              {tools.length} available
            </div>
          )}
        </div>
        
        {visibleTools.length > 0 ? (
          <div className="space-y-4">
            {visibleTools.map((tool) => (
              <div key={tool.id} className="bg-gray-50 dark:bg-gray-900/60 border border-gray-100 dark:border-gray-800 rounded-md p-4">
                <h3 className="font-medium text-foreground mb-1">{tool.name}</h3>
                <p className="text-muted-foreground text-sm">{tool.description}</p>
              </div>
            ))}
            
            {hasMoreTools && (
              <div className="flex justify-center mt-4">
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => setShowAllTools(!showAllTools)}
                >
                  {showAllTools ? "Show Less" : `Show ${tools.length - 4} More`}
                </Button>
              </div>
            )}
          </div>
        ) : (
          <div className="py-8 text-center text-muted-foreground">
            <p>No tools available for this MCP</p>
          </div>
        )}
      </div>
    </div>
  );
}
