'use client';

import { X } from "lucide-react";
import { useState, useEffect } from "react";
import { useSidebar } from "@/components/ui/sidebar";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent } from "@/components/ui/dialog";

export function FlowsAnnouncement() {
  const [isVisible, setIsVisible] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const { state } = useSidebar();

  useEffect(() => {
    const isAnnouncementClosed = localStorage.getItem('feature_announcement_closed');
    if (!isAnnouncementClosed) {
      setIsVisible(true);
    }
  }, []);

  const handleClose = (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsVisible(false);
    localStorage.setItem('feature_announcement_closed', 'true');
  };

  if (!isVisible || state === 'collapsed') return null;

  return (
    <>
      <Card 
        className="mx-3 mb-2 relative cursor-pointer group shadow-none border"
        style={{ maxWidth: '240px' }}
        onClick={() => setDialogOpen(true)}
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
          <h4 className="text-sm font-medium mb-1">New Feature</h4>
          <p className="text-xs text-muted-foreground leading-snug mb-2">
            Create any workflow you want with our new Flow feature. 
          </p>
          <p className="text-xs font-medium text-primary hover:opacity-80 transition-opacity">
            Learn more
          </p>
        </div>
      </Card>
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="sm:max-w-[800px] p-0">
          <div className="aspect-video">
            <iframe
              width="100%"
              height="100%"
              src="https://www.youtube.com/embed/rDYBVFQ8izI"
              title="Flows Announcement"
              frameBorder="0"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
            />
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
} 