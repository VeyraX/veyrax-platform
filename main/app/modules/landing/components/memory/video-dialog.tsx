"use client";

import { useState } from "react";
import { Dialog, DialogContent, DialogTrigger } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Play } from "lucide-react";

interface VideoDialogProps {
  videoSrc: string;
  children: React.ReactNode;
}

export const VideoDialog = ({ videoSrc, children }: VideoDialogProps) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        {children}
      </DialogTrigger>
      <DialogContent 
        className="sm:max-w-[80vw] max-h-[80vh] p-0 overflow-hidden bg-black"
        closeButtonClassName="text-white hover:text-white/90"
      >
        <video 
          src={videoSrc} 
          controls 
          autoPlay 
          className="w-full h-full object-contain"
          onEnded={() => setIsOpen(false)}
        />
      </DialogContent>
    </Dialog>
  );
};

export default VideoDialog;