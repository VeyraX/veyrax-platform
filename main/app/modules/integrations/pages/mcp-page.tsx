'use client'

import { FC, useState, useEffect } from 'react'
import { McpCard } from '../components/mcp/mcp-card'
import { Header } from '@/app/modules/general/components/header'
import { Skeleton } from "@/components/ui/skeleton"
import { Button } from "@/components/ui/button"
import { McpDetails, GitHubRepoInfo, UserMcpEnvironment } from "../api/types.integrations.mcp"
import { createClient } from '@/lib/utils/supabase/client'
import { User } from '@supabase/supabase-js'
import { getSingleMcpRepositoryData } from '../api/api.integrations.mcp'

interface McpPageProps {
  isPublic?: boolean
  hideHeader?: boolean
  mcpRepositories?: McpRepositoryData[]
  isLoading?: boolean
  onConnectionUpdate?: () => Promise<void>
  searchQuery?: string
}

interface McpRepositoryData {
  mcpDetails: McpDetails;
  repoInfo: GitHubRepoInfo | null;
  userEnvironment: UserMcpEnvironment | null;
  isConnected: boolean;
}

const McpPage: FC<McpPageProps> = ({ 
  isPublic = false, 
  hideHeader = false,
  mcpRepositories: externalMcpRepositories = [],
  isLoading: externalIsLoading = false,
  onConnectionUpdate,
  searchQuery = ""
}) => {
  const supabase = createClient();
  const [mcpRepositories, setMcpRepositories] = useState<McpRepositoryData[]>([])
  const [filteredMcpRepositories, setFilteredMcpRepositories] = useState<McpRepositoryData[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [categories, setCategories] = useState<string[]>(["All"])
  const [selectedCategory, setSelectedCategory] = useState<string>("All")
  const [currentUser, setCurrentUser] = useState<User | null>(null);

  useEffect(() => {
    const fetchUser = async () => {
      const { data: { user } } = await supabase.auth.getUser();
      setCurrentUser(user);
    };
    fetchUser();
  }, [supabase]);

  useEffect(() => {
    setMcpRepositories(externalMcpRepositories);
    setFilteredMcpRepositories(externalMcpRepositories);

    const generatedCategories = new Set<string>();
    generatedCategories.add("All");
    if (!isPublic) {
      generatedCategories.add("My Connections");
      generatedCategories.add("My Deployments");
    }
    setCategories(Array.from(generatedCategories));

  }, [externalMcpRepositories, isPublic]);
  
  useEffect(() => {
    setIsLoading(externalIsLoading);
  }, [externalIsLoading]);

  useEffect(() => {
    let filtered = [...mcpRepositories];
    
    if (searchQuery.trim() !== "") {
      const query = searchQuery.toLowerCase().trim();
      
      filtered = filtered.filter(repo => {
        if (repo.mcpDetails.name.toLowerCase().includes(query)) return true;
        
        if (repo.mcpDetails.description && repo.mcpDetails.description.toLowerCase().includes(query)) return true;
        
        if (repo.mcpDetails.input_schema && Array.isArray(repo.mcpDetails.input_schema)) {
          const toolNames = repo.mcpDetails.input_schema.map(tool => tool.name?.toLowerCase() || '');
          if (toolNames.some(name => name.includes(query))) return true;
        }
        
        return false;
      });
    }
    
    if (!isPublic && selectedCategory === "My Connections") {
      filtered = filtered.filter(repo => repo.isConnected === true);
    } else if (!isPublic && selectedCategory === "My Deployments") {
      filtered = filtered.filter(repo => repo.mcpDetails.author_user_id === currentUser?.id);
    }
    
    setFilteredMcpRepositories(filtered);
  }, [searchQuery, selectedCategory, mcpRepositories, currentUser, isPublic]);

  const handleMcpConnectionUpdate = async () => {
    if (onConnectionUpdate) {
      await onConnectionUpdate();
    }
  };

  const handleSingleMcpUpdate = async (repositoryId: string) => {
    if (!repositoryId) return;
    
    try {
      const updatedRepoData = await getSingleMcpRepositoryData(repositoryId);
      console.log(updatedRepoData);
      
      if (updatedRepoData) {
        setMcpRepositories(prev => {
          return prev.map(repo => {
            if (repo.mcpDetails.id === repositoryId) {
              return updatedRepoData;
            }
            return repo;
          });
        });
      }
    } catch (error) {
      console.error("Error updating single MCP repository:", error);
    }
  };

  const handleCategoryClick = (category: string) => {
    setSelectedCategory(category);
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
    <div className={`flex-1 flex flex-col relative ${!hideHeader ? 'h-[100vh]' : ''} w-full`}>
      {!hideHeader && !isPublic && <Header isShowChat={false} />}

      <div className={`flex-1 ${!hideHeader ? 'px-8 py-6' : 'p-0'}`}>
        {!hideHeader && (
          <div className="mb-6">
            <h1 className="text-3xl font-bold tracking-tight">MCP Repositories</h1>
          </div>
        )}
        
        {!isPublic && (
          <div className="relative mb-4">
            <div className="max-w-[calc(100vw-4rem)] overflow-x-auto h-12 [&::-webkit-scrollbar]:hidden [-ms-overflow-style:none] [scrollbar-width:none] relative">
              <div className="flex space-x-3 pb-2">
                {categories.map(category => (
                  <Button
                    key={category}
                    variant={selectedCategory === category ? "default" : "outline"}
                    size="default"
                    className="rounded-full whitespace-nowrap px-4 font-medium flex-shrink-0"
                    onClick={() => handleCategoryClick(category)}
                  >
                    {category}
                  </Button>
                ))}
              </div>
            </div>
          </div>
        )}
        
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {isLoading ? (
            [...Array(9)].map((_, index) => (
              <McpSkeleton key={`mcp-skeleton-${index}`} />
            ))
          ) : (
            <>
              {filteredMcpRepositories.length > 0 ? (
                filteredMcpRepositories.map((repo) => (
                  <McpCard 
                    key={repo.mcpDetails.id}
                    imageName={repo.mcpDetails.image_name}
                    mcpDetails={repo.mcpDetails}
                    isConnected={repo.isConnected}
                    userEnvironment={repo.userEnvironment}
                    onConnectionUpdate={handleMcpConnectionUpdate}
                    onSingleMcpUpdate={handleSingleMcpUpdate}
                    repoInfo={repo.repoInfo}
                    isPublic={isPublic}
                  />
                ))
              ) : (
                <div className="col-span-full text-center py-8">
                  <p className="text-muted-foreground">
                    {searchQuery.trim() || selectedCategory !== "All" 
                      ? "No MCP repositories found matching your filters." 
                      : "No MCP repositories available."}
                  </p>
                  {selectedCategory === "My Connections" && !searchQuery.trim() && (
                    <p className="mt-2 text-sm text-muted-foreground">
                      You haven't connected any MCPs yet.
                    </p>
                  )}
                   {selectedCategory === "My Deployments" && !searchQuery.trim() && (
                    <p className="mt-2 text-sm text-muted-foreground">
                      You haven't created any MCP deployments yet.
                    </p>
                  )}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}

export default McpPage 