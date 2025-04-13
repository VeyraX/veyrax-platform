"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ArrowLeft } from "lucide-react";
import { Tool, McpDetails, McpViewPageProps, McpDeployment, GitHubRepoInfo } from "@/app/modules/integrations/api/types.integrations.mcp";
import { getMcpDetailsByImageName, getGitHubRepoInfo, getMcpDeployments } from "@/app/modules/integrations/api/api.integrations.mcp";
import { McpOverview } from "../components/mcp/mcp-overview";
import { McpUsage } from "../components/mcp/mcp-installation";
import { McpDocumentation } from "../components/mcp/mcp-documentation";
import { createClient } from '@/lib/utils/supabase/client';
import { McpDeployments } from "../components/mcp/mcp-deployments";
import { McpSettings } from "../components/mcp/mcp-settings";
import { McpHeader } from "../components/mcp/mcp-header";

const supabase = createClient();

export default function McpViewPage({ 
  imageName = "notion-mcp"
}: McpViewPageProps) {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("overview");
  const [tools, setTools] = useState<Tool[]>([]);
  const [mcpDetails, setMcpDetails] = useState<McpDetails | null>(null);
  const [repoInfo, setRepoInfo] = useState<GitHubRepoInfo | null>(null);
  const [isAuthor, setIsAuthor] = useState(false);
  const [deployments, setDeployments] = useState<McpDeployment[]>([]);
  
  useEffect(() => {
    const searchParams = new URLSearchParams(window.location.search);
    const tabParam = searchParams.get('tab');
    
    if (tabParam === 'api') {
      setActiveTab('api');
    } else if (tabParam === 'deployment') {
      setActiveTab('deployment');
    } else if (tabParam === 'settings') {
      setActiveTab('settings');
    } else if (tabParam === 'overview' || !tabParam) {
      setActiveTab('overview');
    }
    
    const fetchAllData = async () => {
      setIsLoading(true);
      try {
        const data = await getMcpDetailsByImageName(imageName);
        
        if (data) {
          setMcpDetails(data);
          
          const { data: { user } } = await supabase.auth.getUser();
          console.log("user", user);
          setIsAuthor(user?.id === data.author_user_id);
          
          if (data.input_schema && Array.isArray(data.input_schema)) {
            const parsedTools = data.input_schema.map((schema, index) => ({
              id: schema.name || `tool-${index}`,
              name: schema.name || `Tool ${index}`,
              description: schema.description || 'No description available'
            }));
            setTools(parsedTools);
          }
          
          if (data.repo_url) {
            try {
              const githubData = await getGitHubRepoInfo(data.repo_url);
              setRepoInfo(githubData);
            } catch (error) {
              console.error("Error fetching GitHub data:", error);
            }
          }
          
          const deploymentData = await getMcpDeployments(data.id);
          setDeployments(deploymentData);
        }
      } catch (error) {
        console.error("Error fetching MCP data:", error);
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchAllData();
  }, [imageName]);
  
  const handleBack = () => {
    router.back();
  };
  
  if (isLoading) {
    return (
      <div className="h-screen overflow-hidden flex flex-col">
        <div className="flex items-center justify-between w-full px-4 py-2 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800">
          <div className="flex items-center gap-2">
            <Skeleton className="w-6 h-6 rounded-full" />
            <Skeleton className="w-40 h-5" />
          </div>
          <Skeleton className="w-20 h-7 rounded-full" />
        </div>
        
        <div className="flex-1 overflow-hidden p-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="space-y-6">
              <div className="bg-white dark:bg-gray-900 rounded-md border border-gray-200 dark:border-gray-800 p-6 space-y-4">
                <Skeleton className="w-32 h-6" />
                <Skeleton className="w-full h-40" />
              </div>
              
              <div className="bg-white dark:bg-gray-900 rounded-md border border-gray-200 dark:border-gray-800 p-6 space-y-4">
                <Skeleton className="w-24 h-6" />
                <Skeleton className="w-full h-20" />
              </div>
            </div>
            
            <div className="flex flex-col space-y-6">
              <div className="bg-white dark:bg-gray-900 rounded-md border border-gray-200 dark:border-gray-800 p-6 space-y-4">
                <Skeleton className="w-32 h-6" />
                <div className="space-y-3">
                  <Skeleton className="w-full h-16" />
                  <Skeleton className="w-full h-16" />
                  <Skeleton className="w-full h-16" />
                </div>
              </div>

              <div className="bg-white dark:bg-gray-900 rounded-md border border-gray-200 dark:border-gray-800 p-6">
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <Skeleton className="w-32 h-6" />
                    <Skeleton className="w-8 h-8 rounded-full" />
                  </div>
                  <Skeleton className="w-full h-40" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Use mcpDetails if available, otherwise fallback to defaults
  const repoName = mcpDetails?.name || "Unknown MCP";
  const mcpId = mcpDetails?.id || "unknown-id";
  const githubUrl = mcpDetails?.repo_url || "#";

  return (
    <div className="h-screen overflow-hidden flex flex-col">
      {/* Header */}
      <McpHeader 
        repoName={repoName}
        onBack={handleBack}
        isAuthor={isAuthor}
        repoUrl={githubUrl}
      />
      
      {/* Content */}
      <div className="flex-1 overflow-auto">
        <div className="w-full px-6 py-6">
          <Tabs 
            defaultValue="overview" 
            className="w-full"
            value={activeTab}
            onValueChange={(value) => {
              setActiveTab(value);
              // Update URL query parameter when tab changes
              const url = new URL(window.location.href);
              url.searchParams.set('tab', value);
              window.history.pushState({}, '', url);
            }}
          >
            <div className="mb-6 flex justify-between">
              {/* Left tabs */}
              <TabsList className="h-auto gap-4 rounded-none bg-transparent px-0 py-0 text-foreground">
                <TabsTrigger 
                  className="relative after:absolute after:inset-x-0 after:bottom-0 after:-mb-1 after:h-0.5 hover:bg-accent hover:text-foreground data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:after:bg-primary data-[state=active]:hover:bg-accent" 
                  value="overview"
                >
                  Overview
                </TabsTrigger>
                <TabsTrigger 
                  className="relative after:absolute after:inset-x-0 after:bottom-0 after:-mb-1 after:h-0.5 hover:bg-accent hover:text-foreground data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:after:bg-primary data-[state=active]:hover:bg-accent" 
                  value="api"
                >
                  API
                </TabsTrigger>
              </TabsList>
              
              {/* Right tabs - only for authors */}
              {isAuthor && (
                <TabsList className="h-auto gap-4 rounded-none bg-transparent px-0 py-0 text-foreground">
                  <TabsTrigger 
                    className="relative after:absolute after:inset-x-0 after:bottom-0 after:-mb-1 after:h-0.5 hover:bg-accent hover:text-foreground data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:after:bg-primary data-[state=active]:hover:bg-accent" 
                    value="deployment"
                  >
                    Deployment
                  </TabsTrigger>
                  <TabsTrigger 
                    className="relative after:absolute after:inset-x-0 after:bottom-0 after:-mb-1 after:h-0.5 hover:bg-accent hover:text-foreground data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:after:bg-primary data-[state=active]:hover:bg-accent" 
                    value="settings"
                  >
                    Settings
                  </TabsTrigger>
                </TabsList>
              )}
            </div>

            {/* Tab Content */}
            <TabsContent value="overview" className="mt-0">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="w-full">
                  {/* Left column - Overview Component */}
                  <McpOverview 
                    imageName={imageName}
                    mcpDetails={mcpDetails}
                    tools={tools}
                    mcpId={mcpId}
                    repoName={repoName}
                    githubUrl={githubUrl}
                    deploymentStatus={'Active'}
                    repoInfo={repoInfo}
                  />
                </div>
                
                <div className="space-y-6">
                  {/* Right column - Installation Component */}
                  <McpUsage imageName={imageName} mcpDetails={mcpDetails} />
                </div>
              </div>
            </TabsContent>

            <TabsContent value="api" className="mt-0">
              <McpDocumentation mcpDetails={mcpDetails} tools={tools} />
            </TabsContent>

            <TabsContent value="deployment" className="mt-0">
              <McpDeployments deployments={deployments} repoName={repoName} />
            </TabsContent>

            <TabsContent value="settings" className="mt-0">
              <McpSettings mcpId={mcpId} mcpDetails={mcpDetails} deployments={deployments} />
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
}
