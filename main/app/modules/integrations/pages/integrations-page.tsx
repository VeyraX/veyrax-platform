'use client'

import { FC } from 'react'
import { IntegrationCard } from '../components/integration-card'
import { dummyApiCards } from '../dummy-data.integrations'
import { Header } from '@/app/modules/general/components/header'
const IntegrationsPage: FC = () => {
  return (
    <div className="flex-1 flex flex-col relative h-[100vh] w-full">
      <Header isShowChat={false} />

      <div className="flex-1 px-8 py-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold">Integrations</h1>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {dummyApiCards.map((integration) => (
          <IntegrationCard key={integration.id} {...integration} />
          ))}
        </div>
      </div>
    </div>
  )
}

export default IntegrationsPage
