'use client';

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { McpCard } from "@/app/modules/integrations/components/mcp/mcp-card";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { ArrowLeft, CheckCircle } from "lucide-react";
import { McpDetails, GitHubRepoInfo } from "@/app/modules/integrations/api/types.integrations.mcp";
import { getUserMcpEnvironment, getGitHubRepoInfo } from "@/app/modules/integrations/api/api.integrations.mcp";

interface ExistingMcpCardProps {
  repoUrl: string;
  imageName: string;
  repositoryId: string;
  repoName: string;
  repoDescription: string;
  env: Record<string, string>;
  onBack: () => void;
}

export function ExistingMcpCard({
  repoUrl,
  imageName,
  repositoryId,
  repoName,
  repoDescription,
  env,
  onBack
}: ExistingMcpCardProps) {
  const router = useRouter();
  const [isConnected, setIsConnected] = useState(false);
  const [userEnvironment, setUserEnvironment] = useState<{
    env: Record<string, string>;
    user_id: string;
    repo_id: string;
  } | null>(null);
  
  // useState instead of useRef so the component re-renders once data is loaded
  const [repoInfo, setRepoInfo] = useState<GitHubRepoInfo | null>(null);
  const [dataLoading, setDataLoading] = useState(true);
  
  useEffect(() => {
    let isMounted = true;
    
    const preloadData = async () => {
      if (!repositoryId) return;
      
      try {
        const [userEnv, info] = await Promise.all([
          getUserMcpEnvironment(repositoryId),
          getGitHubRepoInfo(repoUrl)
        ]);
        
        if (!isMounted) return;
        
        if (userEnv) {
          setIsConnected(true);
          setUserEnvironment({
            env: userEnv.env || {},
            user_id: userEnv.user_id,
            repo_id: userEnv.repo_id
          });
        }
        
        console.log("GitHub info loaded:", info);
        setRepoInfo(info);
      } catch (error) {
        console.error("Error during preload:", error);
      } finally {
        if (isMounted) {
          setDataLoading(false);
        }
      }
    };
    
    preloadData();
    
    return () => {
      isMounted = false;
    };
  }, [repositoryId, repoUrl]);
  
  const handleConnectionUpdate = async () => {
    try {
      const userEnv = await getUserMcpEnvironment(repositoryId);
      setIsConnected(!!userEnv);
      
      if (userEnv) {
        setUserEnvironment({
          env: userEnv.env || {},
          user_id: userEnv.user_id,
          repo_id: userEnv.repo_id
        });
        
        router.push(`/integrations/mcp/${imageName}`);
      }
    } catch (error) {
      console.error("Error updating connection:", error);
    }
  };

  const mcpDetails: McpDetails = {
    name: repoName,
    description: repoDescription,
    repo_url: repoUrl,
    id: repositoryId,
    image_name: imageName,
    input_schema: [],
    env: env,
    created_at: new Date().toISOString(),
    author_user_id: null
  };

  return (
    <div className="space-y-6">
      <Alert className="border-green-500 bg-green-50 dark:border-green-800 dark:bg-green-900/20">
        <AlertTitle className="text-green-700 dark:text-green-400">Great news! This MCP is ready to use!</AlertTitle>
        <AlertDescription className="text-green-600 dark:text-green-400">
          {isConnected 
            ? 'You\'re already connected to this MCP. You can manage your connection below.'
            : 'You can connect to it instantly using the card below.'}
        </AlertDescription>
      </Alert>    
      
      <div>
        <McpCard 
          imageName={imageName}
          mcpDetails={mcpDetails}
          isConnected={isConnected}
          userEnvironment={userEnvironment}
          onConnectionUpdate={handleConnectionUpdate}
          repoInfo={repoInfo}
        />
      </div>
      
      <div className="flex justify-between">
        <Button 
          onClick={onBack}
          variant="outline"
          className="px-4 gap-2"
        >
          <ArrowLeft className="h-4 w-4" />
          Back
        </Button>
      </div>
    </div>
  );
}
