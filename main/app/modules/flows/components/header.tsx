import { ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button"; 
import { Skeleton } from "@/components/ui/skeleton";
import { useRouter, usePathname } from "next/navigation";
import { useState } from "react";
import { updateFlowStatus } from "../api/api.flows";
import { Loader2, Copy, Edit } from "lucide-react";

export function FlowHeader({ 
  flowName = "New Flow", 
  onBack, 
  onCreateClick, 
  onPublish,
  isLoading = false,
  flowId,
  isOwner = false
}: { 
  flowName?: string, 
  onBack?: () => void, 
  onCreateClick?: () => void,
  onPublish?: (flowId: string) => void,
  isLoading?: boolean,
  flowId?: string,
  isOwner?: boolean
}) {
  const router = useRouter();
  const pathname = usePathname();
  const isEditMode = pathname?.includes('/edit');
  const [isPublishing, setIsPublishing] = useState(false);
  
  const handlePublish = async () => {
    if (!flowId) {
      onCreateClick?.();
      return;
    }
    
    try {
      setIsPublishing(true);
      await updateFlowStatus(flowId, "Active");
      onPublish?.(flowId);
      // Redirect to view subpath after publishing
      router.push(`/flow/${flowId}/view`);
    } catch (error) {
      console.error("Error publishing flow:", error);
    } finally {
      setIsPublishing(false);
    }
  };

  const handleEditClick = () => {
    if (flowId) {
      router.push(`/flow/${flowId}/edit`);
    }
  };

  const handleCloneClick = () => {
    // Логика клонирования
    // ...
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
        <button onClick={onBack} className="text-gray-700 p-1 rounded-full hover:bg-gray-100">
          <ArrowLeft size={16} />
        </button>
        <div className="flex items-center text-sm">
          <span className="font-medium text-gray-900">{flowName}</span>
        </div>
      </div>
      
      <div className="flex items-center gap-2">
        {isEditMode && flowId && (
          <Button 
            onClick={handlePublish}
            className="rounded-full bg-black text-white text-xs px-3 py-0.5 h-7 hover:bg-gray-800 flex items-center gap-1"
            disabled={isPublishing}
          >
            {isPublishing ? (
              <>
                <Loader2 size={14} className="animate-spin" />
                Publishing...
              </>
            ) : (
              'Publish'
            )}
          </Button>
        )}
        
        {isOwner && !isEditMode ? (
          <Button 
            onClick={handleEditClick}
            className="rounded-full bg-black text-white text-xs px-3 py-0.5 h-7 hover:bg-gray-800 flex items-center gap-1"
          >
            Edit
          </Button>
        ) : !isEditMode && (
          <Button 
            onClick={handleCloneClick}
            className="rounded-full bg-black text-white text-xs px-3 py-0.5 h-7 hover:bg-gray-800 flex items-center gap-1"
          >
            Clone
          </Button>
        )}
      </div>
    </div>
  );
}
