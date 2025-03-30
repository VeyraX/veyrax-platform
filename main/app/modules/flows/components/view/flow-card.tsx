'use client'

import React, { useEffect, useState } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { UserFlow } from '../../api/types.flows'
import { Badge } from '@/components/ui/badge'
import { useRouter } from 'next/navigation'
import { Skeleton } from '@/components/ui/skeleton'
import { getFlowActions, getUserActions, cloneFlow } from '../../api/api.flows'
import { ProviderAction } from '../../api/types.flows'
import { Button } from '@/components/ui/button'
import { Play, MoreHorizontal } from 'lucide-react'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { deleteFlow, updateFlowStatus } from '../../api/api.flows'
import { toast } from 'sonner'

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

interface FlowCardProps extends Omit<UserFlow, 'status' | 'is_shared' | 'is_template'> {
  onFlowChange?: () => void
  isPublishing?: boolean
  status?: 'Active' | 'Draft'
  is_shared?: boolean
  is_template?: boolean
  schedule?: any
  flowTools: ProviderAction[]
}

const FlowCard: React.FC<FlowCardProps> = ({
  id,
  name,
  plain_description,
  isPublishing,
  onFlowChange,
  status = 'Draft',
  is_shared = false,
  schedule,
  flowTools,
  is_template
}) => {
  const router = useRouter()
  const [currentStatus, setCurrentStatus] = useState(status)
  const [isShared, setIsShared] = useState(is_shared)
  const [isDuplicating, setIsDuplicating] = useState(false)
  
  const handleEdit = () => {
    router.push(`/flow/${id}/edit`)
  }

  const handleView = () => {
    if (is_template) {
      router.push(`/flow/${id}/shared`)
    } else {
      router.push(`/flow/${id}/view`)
    }
  }

  const handleDelete = async () => {
    try {
      await deleteFlow(id)
      toast.success('Flow deleted successfully')
      onFlowChange?.()
    } catch (error) {
      toast.error('Failed to delete flow')
      console.error('Error deleting flow:', error)
    }
  }

  const handleStatusChange = async (newStatus: 'Active' | 'Draft') => {
    try {
      await updateFlowStatus(id, newStatus)
      setCurrentStatus(newStatus)
      toast.success(`Flow is now ${newStatus}`)
      onFlowChange?.()
    } catch (error) {
      console.error('Error updating flow status:', error)
      toast.error('Failed to update flow status')
    }
  }

  const handleDuplicate = async () => {
    if (!id) return;
    
    try {
      setIsDuplicating(true);
      const newFlowId = await cloneFlow(id);
      onFlowChange?.();
      router.push(`/flow/${newFlowId}/edit`);
    } catch (error) {
      console.error('Error duplicating flow:', error);
      toast.error(error instanceof Error ? error.message : 'Failed to duplicate the flow');
    } finally {
      setIsDuplicating(false);
    }
  };

  const formatSchedule = (schedule: any) => {
    if (!schedule) return null
    
    const formatTime = (time: string) => {
      const [hours, minutes] = time.split(':');
      const hour = parseInt(hours);
      const ampm = hour >= 12 ? 'PM' : 'AM';
      const hour12 = hour % 12 || 12;
      return `${hour12}${minutes !== '00' ? ':' + minutes : ''} ${ampm}`;
    };
    
    if (schedule.type === 'once') {
      const date = new Date(schedule.oneTime.datetime);
      return `Once at ${formatTime(date.toTimeString().slice(0, 5))}`;
    }
    
    if (schedule.recurrence) {
      const { dayOfWeek, dayOfMonth, time } = schedule.recurrence;
      if (dayOfWeek !== undefined) {
        const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
        return `Every ${days[dayOfWeek]} at ${formatTime(time)}`;
      }
      if (dayOfMonth !== undefined) {
        return `Monthly on day ${dayOfMonth} at ${formatTime(time)}`;
      }
      return `Daily at ${formatTime(time)}`;
    }
    
    return null;
  }

  const truncatedDescription = plain_description 
    ? plain_description.length > 60 
      ? plain_description.substring(0, 60) + '...' 
      : plain_description
    : 'No description'

  return (
    <Card className="w-full shadow-none rounded-lg h-[204px]">
      <CardContent className="p-4 h-full flex flex-col">
        <div className="flex justify-between items-start mb-3">
          <div className="flex items-center gap-2 min-h-[24px] min-w-[72px]">
            {flowTools.slice(0, 3).map((tool) => (
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
          </div>
          <div className="flex items-center gap-2">
            {isPublishing && !is_template && (
              <Badge variant="secondary" className="bg-amber-50 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300">
                Publishing
              </Badge>
            )}
            {!is_template && (
              <Badge variant="secondary" className={`transition-colors text-xs ${
                currentStatus === 'Active' 
                  ? 'bg-green-50 text-green-700 dark:bg-green-900/30 dark:text-green-300' 
                  : 'bg-gray-50 text-gray-600 dark:bg-gray-900/30 dark:text-gray-300'
              }`}>
                {currentStatus}
              </Badge>
            )}
          </div>
        </div>

        <div className="flex justify-between items-center mb-2">
          <h3 className="font-medium text-base">{name}</h3>
        </div>

        <div className="flex-grow">
          <p className="text-sm text-muted-foreground">{truncatedDescription}</p>
        </div>

        <div className="flex justify-between items-center mt-3">
          {!is_template && schedule && (
            <div className="text-xs text-muted-foreground">
              {formatSchedule(schedule)}
            </div>
          )}
          {is_template && (
            <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
              <span>by</span>
              <div className="flex items-center gap-1">
                <img src="/logo.svg" alt="VeyraX" className="w-3.5 h-3.5" />
                <span className="font-medium">VeyraX</span>
              </div>
            </div>
          )}
          <div className="flex items-center gap-2 ml-auto">
            <Button 
              variant="outline" 
              size="sm"
              onClick={handleView}
              className="text-xs"
            >
              View
            </Button>
            {!is_template && (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                    <MoreHorizontal className="h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuItem onClick={handleEdit}>
                    Edit
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={handleDuplicate} disabled={isDuplicating}>
                    {isDuplicating ? 'Duplicating...' : 'Duplicate'}
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => handleStatusChange(currentStatus === 'Active' ? 'Draft' : 'Active')}>
                    {currentStatus === 'Active' ? 'Disable' : 'Activate'}
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={handleDelete} className="text-red-600">
                    Delete
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export default FlowCard 