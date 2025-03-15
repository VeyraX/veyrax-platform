'use client'

import { FC, useState, useEffect } from 'react'
import { IntegrationCard } from '../components/integration-card'
import { Header } from '@/app/modules/general/components/header'
import { Skeleton } from "@/components/ui/skeleton"
import { getIntegrationsData } from '../api/api.integrations'
import { IntegrationCardProps } from '../api/types.integrations'

interface IntegrationsPageProps {
  isPublic?: boolean
  hideHeader?: boolean
}

const IntegrationsPage: FC<IntegrationsPageProps> = ({ isPublic = false, hideHeader = false }) => {
  const [integrations, setIntegrations] = useState<IntegrationCardProps[]>([])
  const [isLoading, setIsLoading] = useState(true)

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
      
      setIntegrations(sortedData)
    } catch (error) {
      console.error('Failed to fetch integrations:', error)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchIntegrations()
  }, [])

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
        <div className="mb-8">
          <h1 className="text-3xl font-bold tracking-tight">{isPublic ? "Marketplace" : "Integrations"}</h1>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {isLoading ? (
            [...Array(8)].map((_, index) => (
              <IntegrationSkeleton key={index} />
            ))
          ) : (
            integrations?.map((integration) => (
              <IntegrationCard 
                key={integration.id} 
                {...integration} 
                onConnectionChange={fetchIntegrations}
                isPublic={isPublic}
              />
            ))
          )}
        </div>
      </div>
    </div>
  )
}

export default IntegrationsPage
