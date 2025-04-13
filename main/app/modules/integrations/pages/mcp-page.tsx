'use client'

import { FC, useState, useEffect } from 'react'
import { McpCard } from '../components/mcp/mcp-card'
import { Header } from '@/app/modules/general/components/header'
import { Skeleton } from "@/components/ui/skeleton"
import { getAllMcpRepositories, getGitHubRepoInfo, getUserMcpEnvironment } from '../api/api.integrations.mcp'
import { McpDetails, GitHubRepoInfo, UserMcpEnvironment } from "../api/types.integrations.mcp"

interface McpPageProps {
  isPublic?: boolean
  hideHeader?: boolean
}

interface McpRepositoryData {
  mcpDetails: McpDetails;
  repoInfo: GitHubRepoInfo | null;
  userEnvironment: UserMcpEnvironment | null;
  isConnected: boolean;
}

const McpPage: FC<McpPageProps> = ({ isPublic = false, hideHeader = false }) => {
  const [mcpRepositories, setMcpRepositories] = useState<McpRepositoryData[]>([])
  const [isLoading, setIsLoading] = useState(true)

  const fetchMcpRepositories = async () => {
    setIsLoading(true)
    try {
      const mcpData = await getAllMcpRepositories();
      
      const mcpDetailsWithInfo = await Promise.all(
        mcpData.map(async (repo) => {
          // Fetch GitHub repo info if available
          const repoInfo = repo.repo_url ? await getGitHubRepoInfo(repo.repo_url) : null;
          
          // Fetch user environment if user is logged in
          const userEnvironment = !isPublic ? await getUserMcpEnvironment(repo.id) : null;
          
          return {
            mcpDetails: repo,
            repoInfo,
            userEnvironment,
            isConnected: !!userEnvironment,
          };
        })
      );
      
      setMcpRepositories(mcpDetailsWithInfo);
    } catch (error) {
      console.error('Failed to fetch MCP repositories:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchMcpRepositories()
  }, [])

  const handleMcpConnectionUpdate = async () => {
    await fetchMcpRepositories();
  };

  const McpSkeleton = () => (
    <div className="p-6 border rounded-lg space-y-4">
      <Skeleton className="h-12 w-12 rounded-full" />
      <Skeleton className="h-4 w-[250px]" />
      <Skeleton className="h-4 w-[200px]" />
      <Skeleton className="h-10 w-[100px]" />
    </div>
  )

  return (
    <div className="flex-1 flex flex-col relative h-[100vh] w-full">
      {!isPublic && <Header isShowChat={false} />}

      <div className="flex-1 px-8 py-6">
        <div className="mb-6">
          <h1 className="text-3xl font-bold tracking-tight">MCP Repositories</h1>
        </div>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {isLoading ? (
            [...Array(8)].map((_, index) => (
              <McpSkeleton key={`mcp-skeleton-${index}`} />
            ))
          ) : mcpRepositories.length > 0 ? (
            mcpRepositories.map((repo) => (
              <McpCard 
                key={repo.mcpDetails.id}
                imageName={repo.mcpDetails.image_name}
                mcpDetails={repo.mcpDetails}
                isConnected={repo.isConnected}
                userEnvironment={repo.userEnvironment}
                onConnectionUpdate={handleMcpConnectionUpdate}
                repoInfo={repo.repoInfo}
                isPublic={isPublic}
              />
            ))
          ) : (
            <div className="col-span-full text-center py-8">
              <p className="text-muted-foreground">No MCP repositories found.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default McpPage 