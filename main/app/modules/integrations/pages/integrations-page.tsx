'use client'

import { FC } from 'react'
import { IntegrationCard } from '../components/integration-card'
import { Header } from '@/app/modules/general/components/header'
import { Skeleton } from "@/components/ui/skeleton"
import { useGetProviders } from '../api/quries.integrations'

const IntegrationsPage: FC = () => {
  const { data: integrations, isLoading, refetch } = useGetProviders()

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
      <Header isShowChat={false} />

      <div className="flex-1 px-8 py-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold">Integrations</h1>
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
                onConnectionChange={refetch}
              />
            ))
          )}
        </div>
      </div>
    </div>
  )
}

export default IntegrationsPage
