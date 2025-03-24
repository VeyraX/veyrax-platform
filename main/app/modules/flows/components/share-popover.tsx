import React, { useState, useEffect, useRef } from "react";
import { 
  Popover, 
  PopoverContent, 
  PopoverTrigger 
} from "@/components/ui/popover";
import { Button } from "@/components/ui/button";
import { Share2, Check, Twitter, Linkedin, Facebook, Link } from "lucide-react";
import { updateFlow } from "../api/api.flows";
import { toast } from "sonner";

interface SharePopoverProps {
  flowId: string;
  isShared: boolean;
  onShareStatusChange?: (isShared: boolean) => void;
}

export function SharePopover({ flowId, isShared, onShareStatusChange }: SharePopoverProps) {
  const [open, setOpen] = useState(false);
  const [isToggling, setIsToggling] = useState(false);
  const [isCopying, setIsCopying] = useState(false);
  const [currentIsShared, setCurrentIsShared] = useState(isShared);
  const linkRef = useRef<HTMLParagraphElement>(null);
  
  useEffect(() => {
    setCurrentIsShared(isShared);
  }, [isShared]);
  
  const baseUrl = typeof window !== 'undefined' ? `${window.location.origin}/flow/` : '';
  const shareUrl = `${baseUrl}${flowId}/shared`;
  
  const handleCopyLink = async () => {
    try {
      setIsCopying(true);
      await navigator.clipboard.writeText(shareUrl);
    } catch (error) {
      console.error("Error copying:", error);
    } finally {
      setTimeout(() => setIsCopying(false), 1000);
    }
  };
  
  const toggleSharing = async () => {
    try {
      setIsToggling(true);
      const newIsShared = !currentIsShared;
      
      await updateFlow({
        id: flowId,
        is_shared: newIsShared
      });
      
      setCurrentIsShared(newIsShared);
      onShareStatusChange?.(newIsShared);
      
    } catch (error) {
      console.error("Error toggling share status:", error);
      toast.error("Failed to update sharing settings");
    } finally {
      setIsToggling(false);
    }
  };

  const shareToTwitter = () => {
    const text = "Check out this flow I created:";
    const url = `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(shareUrl)}`;
    window.open(url, '_blank');
  };

  const shareToLinkedIn = () => {
    const url = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(shareUrl)}`;
    window.open(url, '_blank');
  };

  const shareToFacebook = () => {
    const url = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(shareUrl)}`;
    window.open(url, '_blank');
  };

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button 
          size="sm"
        >
          Share
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-72 p-3" align="end">
        <div className="flex flex-col space-y-3">
          <div className="space-y-1">
            <h3 className="text-sm font-medium">Share Flow</h3>
            <p className="text-xs text-gray-500">
              {currentIsShared 
                ? "Share the flow with your friends" 
                : "Make this flow shared to anyone"}
            </p>
          </div>
          
          {!currentIsShared ? (
            <Button
              size="sm"
              variant="default"
              disabled={isToggling}
              onClick={toggleSharing}
              className="h-9 w-full"
            >
              {isToggling ? "Making public..." : "Make Public"}
            </Button>
          ) : (
            <>
              <div className="flex justify-between space-x-2">
                <Button
                  size="sm"
                  variant="outline"
                  className="h-9 w-9 p-0 flex-1"
                  onClick={shareToTwitter}
                  title="Share on Twitter"
                >
                  <Twitter size={16} />
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  className="h-9 w-9 p-0 flex-1"
                  onClick={shareToLinkedIn}
                  title="Share on LinkedIn"
                >
                  <Linkedin size={16} />
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  className="h-9 w-9 p-0 flex-1"
                  onClick={shareToFacebook}
                  title="Share on Facebook"
                >
                  <Facebook size={16} />
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  className="h-9 w-9 p-0 flex-1"
                  onClick={handleCopyLink}
                  disabled={isCopying}
                  title="Copy link to clipboard"
                >
                  {isCopying ? <Check size={16} /> : <Link size={16} />}
                </Button>
              </div>

              <div 
                className="w-full overflow-x-auto border rounded-md px-3 py-2 text-sm bg-gray-50" 
                style={{ 
                  msOverflowStyle: 'none', 
                  scrollbarWidth: 'none',
                  WebkitOverflowScrolling: 'touch'
                }}
              >
                <p ref={linkRef} className="text-xs whitespace-nowrap">{shareUrl}</p>
              </div>

              <div className="h-px bg-gray-200 my-1"></div>
              
              <Button
                size="sm"
                variant="outline"
                disabled={isToggling}
                onClick={toggleSharing}
                className="h-8"
              >
                {isToggling ? "Making private..." : "Make Private"}
              </Button>
            </>
          )}
        </div>
      </PopoverContent>
    </Popover>
  );
}