import { ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button"; 
import { Skeleton } from "@/components/ui/skeleton";
import { useRouter, usePathname } from "next/navigation";
import { useState, useEffect } from "react";
import { updateFlowStatus, cloneFlow } from "../api/api.flows";
import { Loader2, Copy, Edit, LogIn } from "lucide-react";
import { SharePopover } from "./share-popover";
import { toast } from "sonner";

export function FlowHeader({ 
  flowName = "New Flow", 
  onBack, 
  onCreateClick, 
  onPublish,
  isLoading = false,
  flowId,
  isOwner = false,
  isShared = false,
  isAuthenticated = true
}: { 
  flowName?: string, 
  onBack?: () => void, 
  onCreateClick?: () => void,
  onPublish?: (flowId: string) => void,
  isLoading?: boolean,
  flowId?: string,
  isOwner?: boolean,
  isShared?: boolean,
  isAuthenticated?: boolean
}) {
  const router = useRouter();
  const pathname = usePathname();
  const isEditMode = pathname?.includes('/edit');
  const isCreateMode = pathname === '/flow/create';
  const [isActivating, setIsActivating] = useState(false);
  const [isCloning, setIsCloning] = useState(false);
  const [currentIsShared, setCurrentIsShared] = useState(isShared);
  
  useEffect(() => {
    setCurrentIsShared(isShared);
  }, [isShared]);
  
  const handleBackClick = () => {
    router.push('/flows');
  };
  
  const handleActivate = async () => {
    if (!flowId && isCreateMode) {
      toast.error("Please save your flow first before activating Read Mode");
      return;
    }
    
    if (!flowId) {
      onCreateClick?.();
      return;
    }
    
    try {
      setIsActivating(true);
      await updateFlowStatus(flowId, "Active");
      onPublish?.(flowId);
      router.push(`/flow/${flowId}/view`);
    } catch (error) {
      console.error("Error activating flow:", error);
    } finally {
      setIsActivating(false);
    }
  };

  const handleEditClick = () => {
    if (flowId) {
      router.push(`/flow/${flowId}/edit`);
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
          ) : isEditMode && (
            <Button 
              onClick={handleActivate}
              size="sm"
              className="rounded-full"
              disabled={isActivating}
            >
              {isActivating ? 'Activating...' : 'Read Mode'}
            </Button>
          )}
          
          {isAuthenticated && isOwner && !isEditMode ? (
            <div className="flex items-center gap-2">
              {/* Share Popover */}
              {flowId && (
                <SharePopover 
                  flowId={flowId} 
                  isShared={currentIsShared}
                  onShareStatusChange={handleShareStatusChange}
                />
              )}
              
              {/* Edit Mode Button */}
              <Button 
                onClick={handleEditClick}
                size="sm"
                className="rounded-full"
              >
                Edit Mode
              </Button>
            </div>
          ) : isAuthenticated && !isEditMode && !isOwner && (
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
          >
            Read Mode
          </Button>
        </div>
      )}
    </div>
  );
}
