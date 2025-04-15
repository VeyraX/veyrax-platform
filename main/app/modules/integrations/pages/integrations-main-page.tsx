'use client'

import { FC, useState, useEffect } from 'react'
import { useSearchParams, useRouter, usePathname } from 'next/navigation'
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Header } from '@/app/modules/general/components/header'
import IntegrationsPage from './integrations-page'
import McpPage from './mcp-page'
import { Search } from "lucide-react"
import { Input } from "@/components/ui/input"
import { getIntegrationsData } from '../api/api.integrations'
import { IntegrationCardProps } from '../api/types.integrations'
import { getAllMcpRepositories, getGitHubRepoInfo, getUserMcpEnvironment } from '../api/api.integrations.mcp'
import { McpDetails, GitHubRepoInfo, UserMcpEnvironment } from "../api/types.integrations.mcp"
import { Skeleton } from "@/components/ui/skeleton"

interface IntegrationsMainPageProps {
  isPublic?: boolean
  hideHeader?: boolean
}

interface McpRepositoryData {
  mcpDetails: McpDetails;
  repoInfo: GitHubRepoInfo | null;
  userEnvironment: UserMcpEnvironment | null;
  isConnected: boolean;
}

const IntegrationsMainPage: FC<IntegrationsMainPageProps> = ({ isPublic = false, hideHeader = false }) => {
  const router = useRouter()
  const pathname = usePathname()
  const searchParams = useSearchParams()
  
  const [searchQuery, setSearchQuery] = useState("")
  const [activeTab, setActiveTab] = useState(searchParams.get('tab') || "direct-integrations")

  const [integrations, setIntegrations] = useState<IntegrationCardProps[]>([])
  const [integrationsLoading, setIntegrationsLoading] = useState(true)
  
  const [mcpRepositories, setMcpRepositories] = useState<McpRepositoryData[]>([])
  const [mcpLoading, setMcpLoading] = useState(true)

  useEffect(() => {
    const tabParam = searchParams.get('tab')
    if (tabParam && (tabParam === 'direct-integrations' || tabParam === 'mcps')) {
      setActiveTab(tabParam)
    } else {
      setActiveTab('direct-integrations') 
    }
  }, [searchParams])

  const fetchIntegrations = async () => {
    setIntegrationsLoading(true)
    try {
      const data = await getIntegrationsData()
      
      const filteredData = data.filter(integration => integration.is_enabled !== false);
      
      const sortedData = [...filteredData].sort((a, b) => {
        if (a.provider_tag === 'integration-request') return -1;
        if (b.provider_tag === 'integration-request') return 1;
        return (b.count_of_users || 0) - (a.count_of_users || 0);
      });

      setIntegrations(sortedData)
    } catch (error) {
      console.error('Failed to fetch integrations:', error)
    } finally {
      setIntegrationsLoading(false)
    }
  }

  const fetchMcpRepositories = async () => {
    setMcpLoading(true)
    try {
      const mcpData = await getAllMcpRepositories();
      
      const mcpDetailsWithInfo = await Promise.all(
        mcpData.map(async (repo) => {
          const repoInfo = (!repo.metadata?.stars && repo.repo_url) 
            ? await getGitHubRepoInfo(repo.repo_url) 
            : null;
          
          const userEnvironment = !isPublic ? await getUserMcpEnvironment(repo.id) : null;
          
          return {
            mcpDetails: repo,
            repoInfo,
            userEnvironment,
            isConnected: !!userEnvironment,
          };
        })
      );
      
      const sortedMcpDetails = mcpDetailsWithInfo.sort((a, b) => {
        const starsA = a.mcpDetails.metadata?.stars ? Number(a.mcpDetails.metadata.stars) : (a.repoInfo?.stars || 0);
        const starsB = b.mcpDetails.metadata?.stars ? Number(b.mcpDetails.metadata.stars) : (b.repoInfo?.stars || 0);
        return starsB - starsA;
      });
      
      setMcpRepositories(sortedMcpDetails);
    } catch (error) {
      console.error('Failed to fetch MCP repositories:', error);
    } finally {
      setMcpLoading(false);
    }
  };

  useEffect(() => {
    fetchIntegrations()
    fetchMcpRepositories()
  }, [])

  const handleConnectionChange = async () => {
    await fetchIntegrations();
  };

  const handleMcpConnectionUpdate = async () => {
    await fetchMcpRepositories();
  };
  
  return (
    <div className="flex-1 flex flex-col relative h-[100vh] w-full">
      {!isPublic && <Header isShowChat={false} />}

      <div className="flex-1 px-8 py-6">
        <div className="mb-6">
          <h1 className="text-3xl font-bold tracking-tight mb-6">{isPublic ? "Marketplace" : "Integrations"}</h1>
          
          <div className="relative w-full max-w-md mb-6">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input 
              type="text"
              placeholder="Search integrations by name, description or category..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 w-full text-sm"
            />
          </div>
          
          <Tabs 
            defaultValue="direct-integrations" 
            className="w-full"
            value={activeTab}
            onValueChange={(value) => {
              setActiveTab(value);
              const current = new URLSearchParams(Array.from(searchParams.entries()));
              current.set('tab', value);
              const search = current.toString();
              const query = search ? `?${search}` : "";
              router.push(`${pathname}${query}`);
            }}
          >
            <div className="mb-6">
              <TabsList className="h-auto gap-4 rounded-none bg-transparent px-0 py-0 text-foreground">
                <TabsTrigger 
                  className="relative after:absolute after:inset-x-0 after:bottom-0 after:-mb-1 after:h-0.5 hover:bg-accent hover:text-foreground data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:after:bg-primary data-[state=active]:hover:bg-accent" 
                  value="direct-integrations"
                >
                  Direct Integrations
                </TabsTrigger>
                <TabsTrigger 
                  className="relative after:absolute after:inset-x-0 after:bottom-0 after:-mb-1 after:h-0.5 hover:bg-accent hover:text-foreground data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:after:bg-primary data-[state=active]:hover:bg-accent" 
                  value="mcps"
                >
                  MCPs
                </TabsTrigger>
              </TabsList>
            </div>

            <TabsContent value="direct-integrations" className="mt-0 px-0">
              <IntegrationsPage 
                isPublic={isPublic} 
                hideHeader={true}
                searchQuery={searchQuery}
                integrations={integrations}
                isLoading={integrationsLoading}
                onConnectionChange={handleConnectionChange}
              />
            </TabsContent>

            <TabsContent value="mcps" className="mt-0 px-0">
              <McpPage 
                isPublic={isPublic} 
                hideHeader={true}
                mcpRepositories={mcpRepositories}
                isLoading={mcpLoading}
                onConnectionUpdate={handleMcpConnectionUpdate}
                searchQuery={searchQuery}
              />
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  )
}

export default IntegrationsMainPage
