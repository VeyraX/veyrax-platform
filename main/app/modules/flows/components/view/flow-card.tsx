'use client'

import React, { useEffect, useState } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { UserFlow } from '../../api/types.flows'
import { Badge } from '@/components/ui/badge'
import { useRouter } from 'next/navigation'
import { Skeleton } from '@/components/ui/skeleton'
import { getFlowActions, getUserActions } from '../../api/api.flows'
import { ProviderAction } from '../../api/types.flows'
import { Button } from '@/components/ui/button'
import { Play } from 'lucide-react'

export const FlowSkeleton = () => (
  <div className="w-full border rounded-lg h-[204px] p-4 space-y-4">
    <div className="flex justify-between">
      <div className="flex gap-2">
        <Skeleton className="h-5 w-5 rounded-full" />
        <Skeleton className="h-5 w-5 rounded-full" />
      </div>
      <Skeleton className="h-5 w-16 rounded-full" />
    </div>
    <Skeleton className="h-6 w-3/4" />
    <Skeleton className="h-4 w-full" />
    <Skeleton className="h-4 w-2/3" />
    <div className="flex justify-end mt-4">
      <Skeleton className="h-8 w-16 rounded-md" />
    </div>
  </div>
)

interface FlowCardProps extends UserFlow {
  onFlowChange?: () => void
  isPublishing?: boolean
}

const FlowCard: React.FC<FlowCardProps> = ({
  id,
  name,
  plain_description,
  status,
  isPublishing,
  onFlowChange
}) => {
  const router = useRouter()
  const [flowTools, setFlowTools] = useState<ProviderAction[]>([])
  const [isLoadingTools, setIsLoadingTools] = useState(false)
  
  useEffect(() => {
    const fetchFlowTools = async () => {
      if (!id) return
      
      setIsLoadingTools(true)
      try {
        const allActions = await getUserActions()
        
        const flowActionIds = await getFlowActions(id)
        
        const toolsUsed = allActions.filter(action => 
          flowActionIds.includes(action.action_id)
        )
        
        const uniqueProviders = new Map()
        toolsUsed.forEach(tool => {
          if (!uniqueProviders.has(tool.provider_id)) {
            uniqueProviders.set(tool.provider_id, tool)
          }
        })
        
        setFlowTools(Array.from(uniqueProviders.values()))
      } catch (error) {
        console.error('Error fetching flow tools:', error)
      } finally {
        setIsLoadingTools(false)
      }
    }
    
    fetchFlowTools()
  }, [id])
  
  const handleView = () => {
    router.push(`/flow/${id}/view`)
  }
  
  const getStatusBadge = () => {
    if (isPublishing) return <Badge className="bg-amber-500 text-xs">Publishing</Badge>
    if (status === 'Active') return <Badge variant="secondary" className="bg-green-50 text-green-700 dark:bg-green-900/30 dark:text-green-300 transition-colors text-xs">Active</Badge>
    return <Badge variant="outline" className="text-xs">Draft</Badge>
  }

  const truncatedDescription = plain_description 
    ? plain_description.length > 100 
      ? plain_description.substring(0, 100) + '...' 
      : plain_description
    : 'No description'

  return (
    <Card className="w-full shadow-none rounded-lg h-[204px]">
      <CardContent className="p-4 h-full flex flex-col">
        <div className="flex justify-between items-center mb-3">
          <div className="flex items-center gap-2">
            {isLoadingTools ? (
              <>
                <Skeleton className="h-6 w-6 rounded-full" />
                <Skeleton className="h-6 w-6 rounded-full" />
              </>
            ) : flowTools.length > 0 ? (
              <>
                {flowTools.slice(0, 3).map((tool, index) => (
                  <div 
                    key={tool.provider_id} 
                    className="h-6 w-6 rounded-full overflow-hidden flex items-center justify-center bg-white border border-gray-200"
                    title={tool.provider_name}
                  >
                    <img 
                      src={tool.logo_url} 
                      alt={tool.provider_name}
                      className="max-h-full max-w-full object-contain"
                    />
                  </div>
                ))}
                {flowTools.length > 3 && (
                  <div className="h-6 w-6 rounded-full bg-muted flex items-center justify-center text-xs">
                    +{flowTools.length - 3}
                  </div>
                )}
              </>
            ) : (
              <span className="text-xs text-muted-foreground">No tools</span>
            )}
          </div>
          {getStatusBadge()}
        </div>
        
        <div className="flex-1 min-w-0">
          <h2 className="text-base md:text-lg font-semibold truncate">{name}</h2>
          <p className="text-muted-foreground mt-1 text-xs sm:text-sm line-clamp-3">
            {truncatedDescription}
          </p>
        </div>

        <div className="flex justify-end mt-3">
          <Button 
            variant="outline" 
            size="sm"
            onClick={handleView}
            className="text-xs"
          >
            View
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}

export default FlowCard 