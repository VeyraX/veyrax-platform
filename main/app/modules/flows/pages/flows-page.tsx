'use client'

import { FC, useState, useEffect } from 'react'
import FlowCard, { FlowSkeleton } from '../components/view/flow-card'
import { Header } from '@/app/modules/general/components/header'
import { getUserFlows } from '../api/api.flows'
import { UserFlow } from '../api/types.flows'

interface FlowsPageProps {
  hideHeader?: boolean
}

const FlowsPage: FC<FlowsPageProps> = ({ hideHeader = false }) => {
  const [flows, setFlows] = useState<UserFlow[]>([])
  const [isLoading, setIsLoading] = useState(true)

  const fetchFlows = async () => {
    setIsLoading(true)
    try {
      const data = await getUserFlows()
      const sortedData = [...data].sort((a, b) => {
        return new Date(b.created_at || '').getTime() - new Date(a.created_at || '').getTime()
      })
      
      setFlows(sortedData)
    } catch (error) {
      console.error('Failed to fetch flows:', error)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchFlows()
  }, [])

  return (
    <div className="flex-1 flex flex-col relative h-[100vh] w-full">
      {!hideHeader && <Header isShowChat={false} />}

      <div className="flex-1 px-8 py-6">
        <div className="mb-6">
          <div className="flex justify-between items-center mb-6">
            <h1 className="text-3xl font-bold tracking-tight">My Flows</h1>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {isLoading ? (
            [...Array(3)].map((_, index) => (
              <FlowSkeleton key={index} />
            ))
          ) : (
            flows.map((flow) => (
              <FlowCard 
                key={flow.id} 
                {...flow} 
                onFlowChange={fetchFlows}
              />
            ))
          )}
        </div>
      </div>
    </div>
  )
}

export default FlowsPage