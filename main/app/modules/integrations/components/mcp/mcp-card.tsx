'use client'

import { FC, useState, useMemo } from 'react'
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ArrowUpRight, Star, Plus, Loader2, Github } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useRouter } from 'next/navigation'
import { McpDetails, GitHubRepoInfo, UserMcpEnvironment } from "@/app/modules/integrations/api/types.integrations.mcp";
import { formatDistanceToNow } from "date-fns";
import { McpManage } from "./mcp-manage";

interface McpCardProps {
  imageName: string;
  mcpDetails: McpDetails | null;
  isConnected?: boolean;
  userEnvironment?: UserMcpEnvironment | null;
  onConnectionUpdate?: () => Promise<void>;
  repoInfo?: GitHubRepoInfo | null;
  isPublic?: boolean;
}

export const McpCard: FC<McpCardProps> = ({
  imageName,
  mcpDetails,
  isConnected = false,
  userEnvironment,
  onConnectionUpdate,
  repoInfo,
  isPublic = false
}) => {
  const router = useRouter();
  const [showManage, setShowManage] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  
  const repoName = mcpDetails?.name || imageName;
  const description = mcpDetails?.description || "No description available";
  const githubUrl = mcpDetails?.repo_url || "";
  const repositoryId = mcpDetails?.id;
  
  // Parse GitHub URL
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
  
  const handleConnect = (e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent card click event
    setShowManage(true);
  };
  
  const handleManageClose = async (connected?: boolean) => {
    setShowManage(false);
    
    if (connected && onConnectionUpdate) {
      await onConnectionUpdate();
    }
  };
  
  const handleCardClick = () => {
    router.push(`/integrations/mcp/${imageName}`);
  };
  
  return (
    <>
      <Card 
        className="w-full shadow-none rounded-lg h-[204px] border cursor-pointer"
        onClick={handleCardClick}
      >
        <CardContent className="p-4 h-full flex flex-col">
          <div className="flex flex-col flex-1">
            <div className="flex justify-between items-center mb-3">
              <h2 className="text-base md:text-lg font-semibold truncate">{repoName}</h2>
              
              {!isPublic && isConnected && (
                <Badge variant="secondary" className="bg-green-50 text-green-700 dark:bg-green-900/30 dark:text-green-300 transition-colors text-xs">
                  Connected
                </Badge>
              )}
            </div>
            
            <div className="flex items-center gap-1 mb-3">
              <Github className="h-3.5 w-3.5 text-muted-foreground" />
              <span className="text-xs text-muted-foreground">
                {owner && repo ? `${owner}/${repo}` : imageName}
              </span>
            </div>
            
            <div className="flex-1 min-w-0">
              <p className="text-muted-foreground text-xs sm:text-sm line-clamp-2">{description}</p>
            </div>
          </div>

          <div className="flex items-center mt-3 pt-3 justify-between gap-2">
            <div className="flex items-center gap-1 text-xs text-muted-foreground">
              {repoInfo?.stars && (
                <div className="flex items-center gap-1">
                  <Star className="h-3 w-3 text-yellow-500" />
                  <span>{repoInfo.stars} stars</span>
                </div>
              )}
            </div>
            
            {!isPublic && (
              isConnected ? (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleConnect}
                  className="text-xs"
                >
                  Manage
                  <ArrowUpRight className="h-3 w-3 ml-1" />
                </Button>
              ) : (
                <Button 
                  variant="outline"
                  size="sm"
                  onClick={handleConnect}
                  disabled={isConnecting}
                  className="text-xs"
                >
                  {isConnecting ? (
                    <Loader2 className="h-3 w-3 animate-spin" />
                  ) : (
                    <>
                      Connect
                      <Plus className="h-3 w-3 ml-1" />
                    </>
                  )}
                </Button>
              )
            )}
          </div>
        </CardContent>
      </Card>

      {/* MCP Manage Dialog */}
      {showManage && (
        <McpManage
          imageName={imageName}
          open={showManage}
          onClose={handleManageClose}
          predefinedEnv={userEnvironment?.env || mcpDetails?.env || {}}
          repositoryId={repositoryId}
          isConnected={isConnected}
          onConnectionUpdate={onConnectionUpdate}
        />
      )}
    </>
  )
}
