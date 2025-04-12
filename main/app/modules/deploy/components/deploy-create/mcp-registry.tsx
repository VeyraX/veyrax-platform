"use client";

import { useState, useEffect } from "react";
import { ExternalMcpRepository } from "../../api/types.deploy";
import { fetchExternalMcpRepositories } from "../../api/api.deploy";
import { McpCard, McpCardSkeleton } from "./mcp-card";
import { Button } from "@/components/ui/button";
import { ChevronDown, Loader2 } from "lucide-react";

interface McpRegistryProps {
  onSelect?: (repoUrl: string) => void;
}

export function McpRegistry({ onSelect }: McpRegistryProps) {
  const [repositories, setRepositories] = useState<ExternalMcpRepository[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const initialPageSize = 6;
  const loadMorePageSize = 50;

  const loadRepositories = async (page: number, append: boolean = false, pageSize: number = initialPageSize) => {
    try {
      if (append) {
        setIsLoadingMore(true);
      } else {
        setIsLoading(true);
      }

      const { data, count } = await fetchExternalMcpRepositories(page, pageSize);
      
      if (append) {
        setRepositories(prev => [...prev, ...data]);
      } else {
        setRepositories(data);
      }
      
      setTotalCount(count);
      setCurrentPage(page);
    } catch (error) {
      console.error("Error loading external MCP repositories:", error);
    } finally {
      setIsLoading(false);
      setIsLoadingMore(false);
    }
  };

  useEffect(() => {
    loadRepositories(1, false, initialPageSize);
  }, []);

  const handleLoadMore = () => {
    loadRepositories(currentPage + 1, true, loadMorePageSize);
  };

  const hasMore = repositories.length < totalCount;

  return (
    <div className="w-full mt-16">
      <h2 className="text-2xl font-medium mb-6">Explore MCPs</h2>
      
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {Array.from({ length: 6 }).map((_, i) => (
            <McpCardSkeleton key={i} />
          ))}
        </div>
      ) : repositories.length === 0 ? (
        <div className="text-center py-4">
          <p className="text-muted-foreground">No repositories found</p>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            {repositories.map((repo) => (
              <McpCard key={repo.id} repository={repo} onSelect={onSelect} />
            ))}
            
            {isLoadingMore && (
              <>
                {Array.from({ length: 3 }).map((_, i) => (
                  <McpCardSkeleton key={`loading-more-${i}`} />
                ))}
              </>
            )}
          </div>
          
          {hasMore && (
            <div className="mt-6 text-center">
              <Button 
                variant="outline" 
                onClick={handleLoadMore} 
                disabled={isLoadingMore}
                className="gap-2"
              >
                {isLoadingMore ? (
                  <>
                    <Loader2 size={14} className="animate-spin" /> 
                    Loading...
                  </>
                ) : (
                  <>
                    Load More <ChevronDown size={14} />
                  </>
                )}
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  );
} 