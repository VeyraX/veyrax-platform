import { FC, useState, useEffect } from 'react'
import { IntegrationCard } from './integration-card'
import { getIntegrationsData } from '../api/api.integrations'
import { IntegrationCardProps } from '../api/types.integrations'
import { Input } from "@/components/ui/input"
import { Search, X } from "lucide-react"
import { Skeleton } from "@/components/ui/skeleton"

interface SimpleIntegrationsListProps {
  onClose?: () => void;
  return_url?: string;
}

export const SimpleIntegrationsList: FC<SimpleIntegrationsListProps> = ({ onClose, return_url }) => {
  const [integrations, setIntegrations] = useState<IntegrationCardProps[]>([])
  const [searchQuery, setSearchQuery] = useState("")
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchIntegrations = async () => {
      try {
        const data = await getIntegrationsData()
        const filtered = data.filter(i => i.is_enabled !== false)
        setIntegrations(filtered)
      } catch (error) {
        console.error('Failed to fetch integrations:', error)
      } finally {
        setIsLoading(false)
      }
    }
    fetchIntegrations()
  }, [])

  const filteredIntegrations = integrations.filter(integration => {
    const query = searchQuery.toLowerCase()
    return integration.name.toLowerCase().includes(query) ||
           integration.description.toLowerCase().includes(query)
  })

  const handleConnectionChange = () => {
    window.location.reload();
  };

  const IntegrationSkeleton = () => (
    <div className="flex flex-col space-y-3 p-4 border rounded-lg">
      <div className="flex items-center space-x-4">
        <Skeleton className="h-10 w-10 rounded-full" />
        <div className="space-y-2">
          <Skeleton className="h-4 w-[150px]" />
          <Skeleton className="h-3 w-[100px]" />
        </div>
      </div>
      <Skeleton className="h-20 w-full" />
      <Skeleton className="h-9 w-full" />
    </div>
  );

  return (
    <div className="flex flex-col h-[600px]">
      <div className="flex items-center justify-between p-4">
        <h2 className="text-xl font-semibold">Add Integration</h2>
      </div>
      
      <div className="p-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input 
            type="text"
            placeholder="Search integrations..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9 w-full"
          />
        </div>
      </div>

      <div className="flex-1 min-h-0 overflow-y-auto overflow-x-hidden p-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-full">
          {isLoading ? (
            <>
              <IntegrationSkeleton />
              <IntegrationSkeleton />
              <IntegrationSkeleton />
              <IntegrationSkeleton />
            </>
          ) : (
            filteredIntegrations.map((integration) => (
              <IntegrationCard 
                key={integration.id} 
                {...integration}
                onConnectionChange={handleConnectionChange}
                return_url={return_url}
              />
            ))
          )}
        </div>
      </div>
    </div>
  )
}