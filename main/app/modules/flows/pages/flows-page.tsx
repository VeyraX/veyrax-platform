'use client'

import { FC, useState, useEffect } from 'react'
import { Header } from '@/app/modules/general/components/header'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Search, Plus } from 'lucide-react'
import { useRouter } from 'next/navigation'
import FlowCard, { FlowSkeleton } from '../components/view/flow-card'
import { getUserFlows, getUserActions, getFlowActions, getPublicTemplates } from '../api/api.flows'
import { getAllFlowSchedules } from '../api/api.schedule.flows'
import { UserFlow } from '../api/types.flows'
import { FlowSchedule } from '../api/types.flows'
import { ProviderAction } from '../api/types.flows'
import { Card, CardContent } from '@/components/ui/card'

interface FlowWithSchedule extends UserFlow {
  schedule?: FlowSchedule | null;
  tools?: ProviderAction[];
}

interface FlowsPageProps {
  hideHeader?: boolean
}

const FlowsPage: FC<FlowsPageProps> = ({ hideHeader = false }) => {
  const router = useRouter()
  const [flows, setFlows] = useState<FlowWithSchedule[]>([])
  const [filteredFlows, setFilteredFlows] = useState<FlowWithSchedule[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedCategory, setSelectedCategory] = useState<string>("My Flows")
  
  const categories = ["Templates", "My Flows", "Active", "Scheduled", "Shared"]

  const fetchFlows = async () => {
    setIsLoading(true)
    try {
      const [userFlows, templates, schedulesData, allActions] = await Promise.all([
        getUserFlows(),
        getPublicTemplates(),
        getAllFlowSchedules(),
        getUserActions()
      ])

      const flowsData = [...userFlows, ...templates]
      const flowIds = flowsData.map(flow => flow.id)
      const flowActionsPromises = flowIds.map(id => getFlowActions(id))
      const flowActionsResults = await Promise.all(flowActionsPromises)
      
      const flowToolsMap = new Map()
      flowActionsResults.forEach((actionIds, index) => {
        const flowId = flowIds[index]
        const toolsUsed = allActions.filter(action => actionIds.includes(action.action_id))
        
        const uniqueProviders = new Map()
        toolsUsed.forEach(tool => {
          if (!uniqueProviders.has(tool.provider_id)) {
            uniqueProviders.set(tool.provider_id, tool)
          }
        })
        
        flowToolsMap.set(flowId, Array.from(uniqueProviders.values()))
      })

      const flowsWithSchedulesAndTools = flowsData.map(flow => ({
        ...flow,
        schedule: schedulesData.find(s => s.flow_id === flow.id)?.schedule,
        tools: flowToolsMap.get(flow.id) || []
      }))

      const sortedData = [...flowsWithSchedulesAndTools].sort((a, b) => {
        return new Date(b.created_at || '').getTime() - new Date(a.created_at || '').getTime()
      })
      
      setFlows(sortedData)
    } catch (error) {
      console.error('Failed to fetch flows:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const filterFlows = (flows: FlowWithSchedule[], query: string, category: string) => {
    let filtered = [...flows]
    
    if (query.trim() !== "") {
      const searchTerm = query.toLowerCase().trim()
      filtered = filtered.filter(flow => {
        if (flow.name.toLowerCase().includes(searchTerm)) return true
        if (flow.plain_description?.toLowerCase().includes(searchTerm)) return true
        return false
      })
    }
    
    switch (category) {
      case "Templates":
        filtered = filtered.filter(flow => flow.is_template === true)
        break
      case "My Flows":
        filtered = filtered.filter(flow => !flow.is_template)
        break
      case "Active":
        filtered = filtered.filter(flow => flow.status === "Active" && !flow.is_template)
        break
      case "Scheduled":
        filtered = filtered.filter(flow => flow.schedule !== null && flow.schedule !== undefined && !flow.is_template)
        break
      case "Shared":
        filtered = filtered.filter(flow => flow.is_shared === true && !flow.is_template)
        break
    }
    
    return filtered
  }

  useEffect(() => {
    fetchFlows()
  }, [])

  useEffect(() => {
    const filtered = filterFlows(flows, searchQuery, selectedCategory)
    setFilteredFlows(filtered)
  }, [flows, searchQuery, selectedCategory])

  const handleCategoryClick = (category: string) => {
    setSelectedCategory(category)
  }

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value)
  }

  return (
    <div className="flex-1 flex flex-col relative h-[100vh] w-full">
      {!hideHeader && <Header isShowChat={false} />}

      <div className="flex-1 px-8 py-6">
        <div className="mb-4">
          <h1 className="text-3xl font-bold tracking-tight mb-6">Flows</h1>
          
          <div className="flex flex-col gap-4">
            <div className="relative w-full max-w-md">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input 
                type="text"
                placeholder="Search flows by name or description..."
                value={searchQuery}
                onChange={handleSearch}
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
          {selectedCategory !== "Templates" && (
            <Card className="w-full shadow-none rounded-lg h-[204px] group">
              <CardContent className="p-4 h-full flex flex-col">
                <div className="flex justify-between items-start mb-3">
                  <div className="flex items-center gap-2 min-h-[24px] min-w-[72px]">
                    <div className="h-6 w-6 rounded-full overflow-hidden flex items-center justify-center bg-primary/10">
                      <Plus className="h-3 w-3 text-primary" />
                    </div>
                  </div>
                </div>
                <div className="flex justify-between items-center mb-2">
                  <h3 className="font-medium text-base group-hover:text-primary transition-colors">New Flow</h3>
                </div>
                <div className="flex-grow">
                  <p className="text-sm text-muted-foreground">Create a new automation flow to streamline your workflow.</p>
                </div>
                <div className="flex justify-end items-center mt-3">
                  <Button variant="outline" size="sm" className="text-xs" onClick={() => router.push('/flow/create')}>
                    Create
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
          {isLoading ? (
            [...Array(8)].map((_, index) => (
              <FlowSkeleton key={index} />
            ))
          ) : filteredFlows.length > 0 ? (
            filteredFlows.map((flow) => (
              <FlowCard
                key={flow.id}
                {...flow}
                flowTools={flow.tools || []}
                onFlowChange={fetchFlows}
              />
            ))
          ) : (
            <div className="col-span-full flex items-center justify-center h-[200px]">
              <p className="text-muted-foreground">No flows found</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default FlowsPage