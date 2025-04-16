'use client';

import { X } from "lucide-react";
import { useState, useEffect } from "react";
import { useSidebar } from "@/components/ui/sidebar";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useRouter } from "next/navigation";

export function FlowsAnnouncement() {
  const [isVisible, setIsVisible] = useState(false);
  const { state } = useSidebar();
  const router = useRouter();

  useEffect(() => {
    const isAnnouncementClosed = localStorage.getItem('feature_deploy_announcement_closed');
    if (!isAnnouncementClosed) {
      setIsVisible(true);
    }
  }, []);

  const handleClose = (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsVisible(false);
    localStorage.setItem('feature_deploy_announcement_closed', 'true');
  };

  if (!isVisible || state === 'collapsed') return null;

  return (
    <Card 
      className="mx-3 mb-2 relative cursor-pointer group shadow-none border"
      style={{ maxWidth: '240px' }}
      onClick={() => router.push('/integrations?tab=mcps')}
    >
      <Button
        variant="ghost"
        size="icon"
        className="absolute right-1.5 top-1.5 h-6 w-6 hover:bg-accent"
        onClick={handleClose}
      >
        <X className="h-3 w-3" />
      </Button>

      <div className="p-3">
        <h4 className="text-sm font-medium mb-1">Deploy and Connect any MCP</h4>
        <p className="text-xs text-muted-foreground leading-snug mb-2">
         You can now deploy and connect any MCP to your VeyraX account.
        </p>
        <p className="text-xs font-medium text-primary hover:opacity-80 transition-opacity">
          Learn more
        </p>
      </div>
    </Card>
  );
} 