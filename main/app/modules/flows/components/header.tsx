import { ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button"; 
import { Skeleton } from "@/components/ui/skeleton";
import { useRouter, usePathname } from "next/navigation";
import { useState, useEffect } from "react";
import { updateFlowStatus, cloneFlow, deleteFlow } from "../api/api.flows";
import { Loader2, MoreVertical } from "lucide-react";
import { SharePopover } from "./share-popover";
import { toast } from "sonner";
import { FlowSchedule } from "../api/types.flows";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Badge } from "@/components/ui/badge";

export function FlowHeader({ 
  flowName = "New Flow", 
  onBack, 
  onCreateClick, 
  onPublish,
  isLoading = false,
  flowId,
  isOwner = false,
  isShared = false,
  isAuthenticated = true,
  hasSchedule = false,
  onActivate,
  isActivating = false,
  initialStatus = 'Draft',
}: { 
  flowName?: string, 
  onBack?: () => void, 
  onCreateClick?: () => void,
  onPublish?: (flowId: string) => void,
  isLoading?: boolean,
  flowId?: string,
  isOwner?: boolean,
  isShared?: boolean,
  isAuthenticated?: boolean,
  hasSchedule?: boolean,
  onActivate?: () => Promise<void>,
  isActivating?: boolean,
  initialStatus?: 'Active' | 'Draft',
}) {
  const router = useRouter();
  const pathname = usePathname();
  const isEditMode = pathname?.includes('/edit');
  const isCreateMode = pathname === '/flow/create';
  const [isCloning, setIsCloning] = useState(false);
  const [currentIsShared, setCurrentIsShared] = useState(isShared);
  const [status, setStatus] = useState<'Active' | 'Draft'>(initialStatus);
  
  useEffect(() => {
    setCurrentIsShared(isShared);
  }, [isShared]);

  useEffect(() => {
    if (initialStatus !== status) {
      setStatus(initialStatus);
    }
  }, [initialStatus]);

  const handleBackClick = () => {
    router.push('/flows');
  };
  
  const handleActivate = async () => {
    if (onActivate) {
      await onActivate();
    } else {
      if (!flowId && isCreateMode) {
        toast.error("Please save your flow first before activating Read Mode");
        return;
      }
      
      if (!flowId) {
        onCreateClick?.();
        return;
      }
      
      try {
        await updateFlowStatus(flowId, "Active");
        onPublish?.(flowId);
        router.push(`/flow/${flowId}/view`);
      } catch (error) {
        console.error("Error activating flow:", error);
        toast.error("Failed to activate flow");
      }
    }
  };

  const handleEditClick = async () => {
    if (flowId) {
      try {
        await updateFlowStatus(flowId, "Draft");
        setStatus('Draft');
        router.push(`/flow/${flowId}/edit`);
      } catch (error) {
        console.error("Error updating flow status:", error);
        toast.error("Failed to update flow status");
      }
    }
  };

  const handleCloneClick = async () => {
    if (!flowId) return;
    
    try {
      setIsCloning(true);
      const newFlowId = await cloneFlow(flowId);
      router.push(`/flow/${newFlowId}/edit`);
    } catch (error) {
      console.error("Error cloning flow:", error);
      toast.error(error instanceof Error ? error.message : "Failed to clone the flow");
    } finally {
      setIsCloning(false);
    }
  };

  const handleLoginClick = () => {
    router.push('/login');
  };

  const handleShareStatusChange = (newIsShared: boolean) => {
    setCurrentIsShared(newIsShared);
  };

  const handleStatusChange = async (newStatus: 'Active' | 'Draft') => {
    if (!flowId) return;
    
    try {
      await updateFlowStatus(flowId, newStatus);
      setStatus(newStatus);
      toast.success(`Flow is now ${newStatus}`);
    } catch (error) {
      console.error('Error updating flow status:', error);
      toast.error('Failed to update flow status');
    }
  };

  const handleDelete = async () => {
    if (!flowId) return;
    
    try {
      await deleteFlow(flowId);
      toast.success('Flow deleted successfully');
      router.push('/flows');
    } catch (error) {
      console.error('Error deleting flow:', error);
      toast.error('Failed to delete flow');
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-between w-full px-4 py-2 bg-white border-b border-gray-200">
        <div className="flex items-center gap-2">
          <Skeleton className="w-6 h-6 rounded-full" />
          <Skeleton className="w-40 h-5" />
        </div>
        <Skeleton className="w-20 h-7 rounded-full" />
      </div>
    );
  }

  return (
    <div className="flex items-center justify-between w-full px-4 py-2 bg-white border-b border-gray-200">
      <div className="flex items-center gap-2">
        {isAuthenticated ? (
          <button onClick={handleBackClick} className="text-gray-700 p-1 rounded-full hover:bg-gray-100">
            <ArrowLeft size={16} />
          </button>
        ) : (
          <div className="w-0 h-0"></div>
        )}
        <div className="flex items-center text-sm">
          <span className="font-medium text-gray-900">{flowName}</span>
          {isOwner && (
            <Badge variant="secondary" className={`ml-2 transition-colors text-xs ${
              status === 'Active' 
                ? 'bg-green-50 text-green-700 dark:bg-green-900/30 dark:text-green-300' 
                : 'bg-gray-50 text-gray-600 dark:bg-gray-900/30 dark:text-gray-300'
            }`}>
              {status}
            </Badge>
          )}
        </div>
      </div>
      
      {!isCreateMode && (
        <div className="flex items-center gap-2">
          {!isAuthenticated ? (
            <Button 
              onClick={handleLoginClick}
              size="sm"
              className="rounded-full"
            >
              Login
            </Button>
          ) : isEditMode ? (
            <>
              <Button 
                onClick={handleActivate}
                size="sm"
                className="rounded-full"
                disabled={isActivating}
              >
                {isActivating ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                  </>
                ) : (
                  'Publish'
                )}
              </Button>
            </>
          ) : isAuthenticated && isOwner ? (
            <div className="flex items-center gap-2">
              {flowId && (
                <>
                  <SharePopover 
                    flowId={flowId} 
                    isShared={currentIsShared}
                    onShareStatusChange={handleShareStatusChange}
                  />
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="icon" className="h-8 w-8">
                        <MoreVertical className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem onClick={handleEditClick}>
                        Edit
                      </DropdownMenuItem>
                      <DropdownMenuItem onClick={() => handleStatusChange(status === 'Active' ? 'Draft' : 'Active')}>
                        {status === 'Active' ? 'Disable' : 'Activate'}
                      </DropdownMenuItem>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem onClick={handleDelete} className="text-red-600">
                        Delete
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </>
              )}
            </div>
          ) : isAuthenticated && !isOwner && (
            <Button 
              onClick={handleCloneClick}
              size="sm"
              className="rounded-full"
              disabled={isCloning}
            >
              {isCloning ? 'Cloning...' : 'Clone'}
            </Button>
          )}
        </div>
      )}

      {isCreateMode && (
        <div className="flex items-center gap-2">
          <Button 
            onClick={handleActivate}
            size="sm"
            className="rounded-full"
            disabled={isActivating}
          >
            {isActivating ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
              </>
            ) : (
              'Publish'
            )}
          </Button>
        </div>
      )}
    </div>
  );
}
