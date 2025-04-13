'use client'

import { FC, useState, useEffect } from 'react'
import { IntegrationCard } from '../components/integration-card'
import { Header } from '@/app/modules/general/components/header'
import { Skeleton } from "@/components/ui/skeleton"
import { getIntegrationsData } from '../api/api.integrations'
import { IntegrationCardProps } from '../api/types.integrations'
import { Input } from "@/components/ui/input"
import { Search } from "lucide-react"
import { Button } from "@/components/ui/button"

interface IntegrationsPageProps {
  isPublic?: boolean
  hideHeader?: boolean
}

const IntegrationsPage: FC<IntegrationsPageProps> = ({ isPublic = false, hideHeader = false }) => {
  const [integrations, setIntegrations] = useState<IntegrationCardProps[]>([])
  const [filteredIntegrations, setFilteredIntegrations] = useState<IntegrationCardProps[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState("")
  const [categories, setCategories] = useState<string[]>([])
  const [selectedCategory, setSelectedCategory] = useState<string>("All")

  const fetchIntegrations = async () => {
    setIsLoading(true)
    try {
      const data = await getIntegrationsData()
      
      const filteredData = data.filter(integration => integration.is_enabled !== false);
      
      const sortedData = [...filteredData].sort((a, b) => {
        if (a.provider_tag === 'integration-request') return -1;
        if (b.provider_tag === 'integration-request') return 1;
        return a.name.localeCompare(b.name);
      });
      
      const allCategories = new Set<string>();
      allCategories.add("All");
      
      if (!isPublic) {
        allCategories.add("My Connections");
      }
      
      allCategories.add("Popular");
      
      sortedData.forEach(integration => {
        if (integration.categories) {
          const cats = integration.categories.split(',').map(cat => cat.trim());
          cats.forEach(cat => {
            if (cat) allCategories.add(cat);
          });
        }
      });
      
      setCategories(Array.from(allCategories));
      setIntegrations(sortedData)
      setFilteredIntegrations(sortedData)
    } catch (error) {
      console.error('Failed to fetch integrations:', error)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchIntegrations()
  }, [])

  useEffect(() => {
    let filtered = [...integrations];
    
    if (searchQuery.trim() !== "") {
      const query = searchQuery.toLowerCase().trim();
      
      filtered = filtered.filter(integration => {
        if (integration.provider_tag === 'integration-request') return true;
        
        if (integration.name.toLowerCase().includes(query)) return true;
        
        if (integration.description.toLowerCase().includes(query)) return true;
        
        if (integration.categories) {
          const categories = integration.categories.split(',').map(cat => cat.trim().toLowerCase());
          if (categories.some(cat => cat.includes(query))) return true;
        }
        
        return false;
      });
    }
    
    if (selectedCategory === "My Connections") {
      filtered = filtered.filter(integration => 
        integration.connected === true || 
        integration.provider_tag === 'integration-request'
      );
    } 
    else if (selectedCategory === "Popular") {
      filtered = filtered.filter(integration => 
        (integration.count_of_users && integration.count_of_users > 0) || 
        integration.provider_tag === 'integration-request'
      );
      
      filtered = filtered.sort((a, b) => (b.count_of_users || 0) - (a.count_of_users || 0));
    }
    else if (selectedCategory !== "All") {
      filtered = filtered.filter(integration => {
        if (integration.provider_tag === 'integration-request') return true;
        
        if (integration.categories) {
          const categories = integration.categories.split(',').map(cat => cat.trim());
          return categories.includes(selectedCategory);
        }
        
        return false;
      });
    }
    
    filtered = filtered.sort((a, b) => {
      if (a.provider_tag === 'integration-request') return -1;
      if (b.provider_tag === 'integration-request') return 1;
      
      if (selectedCategory === "Popular") {
        return (b.count_of_users || 0) - (a.count_of_users || 0);
      }
      
      return 0;
    });
    
    setFilteredIntegrations(filtered);
  }, [searchQuery, selectedCategory, integrations]);

  const handleCategoryClick = (category: string) => {
    setSelectedCategory(category);
  };

  const IntegrationSkeleton = () => (
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
        <div className="mb-4">
          <h1 className="text-3xl font-bold tracking-tight mb-6">{isPublic ? "Marketplace" : "Integrations"}</h1>
          
          <div className="flex flex-col gap-4">
            <div className="relative w-full max-w-md">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input 
                type="text"
                placeholder="Search integrations by name, description or category..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 w-full text-sm"
              />
            </div>
            
            <div className="relative">
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
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {isLoading ? (
            [...Array(8)].map((_, index) => (
              <IntegrationSkeleton key={index} />
            ))
          ) : filteredIntegrations.length > 0 ? (
            filteredIntegrations.map((integration) => (
              <IntegrationCard 
                key={integration.id} 
                {...integration} 
                onConnectionChange={fetchIntegrations}
                isPublic={isPublic}
              />
            ))
          ) : (
            <div className="col-span-full text-center py-8">
              <p className="text-muted-foreground">No integrations found matching your search.</p>
              {selectedCategory === "My Connections" && (
                <p className="mt-2 text-sm text-muted-foreground">
                  You haven't connected any integrations yet.
                </p>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default IntegrationsPage
