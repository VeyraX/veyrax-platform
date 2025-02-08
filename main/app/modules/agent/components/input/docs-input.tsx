"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Link, X, ChevronDown } from "lucide-react";
import { Input } from "@/components/ui/input";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

interface DocsInputProps {
  onAddLink?: (link: string, parseType: 'full' | 'single') => void;
  onRemoveLink?: (link: string) => void;
}

interface DocLink {
  url: string;
  parseType: 'full' | 'single';
}

export function DocsInput({ onAddLink, onRemoveLink }: DocsInputProps) {
  const [links, setLinks] = useState<DocLink[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isOpen, setIsOpen] = useState(false);

  const handleAddLink = (parseType: 'full' | 'single') => {
    if (inputValue.trim()) {
      const newLink = {
        url: inputValue.trim(),
        parseType
      };
      setLinks([...links, newLink]);
      onAddLink?.(inputValue.trim(), parseType);
      setInputValue("");
      setIsOpen(false);
    }
  };

  const handleRemoveLink = (linkToRemove: string) => {
    setLinks(links.filter(link => link.url !== linkToRemove));
    onRemoveLink?.(linkToRemove);
  };

  return (
    <div className="flex flex-wrap items-center gap-2">
      {links.map((link, index) => (
        <div
          key={index}
          className="flex items-center gap-1 bg-black/10 dark:bg-white/10 px-2 py-1 rounded-md text-xs"
        >
          <Link className="w-3 h-3" />
          <span className="max-w-[150px] truncate">{link.url}</span>
          <span className="text-xs text-muted-foreground">
            ({link.parseType})
          </span>
          <Button
            variant="ghost"
            size="icon"
            className="h-4 w-4"
            onClick={() => handleRemoveLink(link.url)}
          >
            <X className="w-3 h-3" />
          </Button>
        </div>
      ))}
      
      <DropdownMenu open={isOpen} onOpenChange={setIsOpen}>
        <DropdownMenuTrigger asChild>
          <Button
            variant="ghost"
            size="sm"
            className="h-7 text-xs"
          >
            <Link className="w-3 h-3 mr-1" />
            Add docs
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="start" className="w-[300px]">
          <div className="px-2 py-2">
            <Input
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              className="h-8 text-xs"
              placeholder="Paste documentation link..."
              onClick={(e) => e.stopPropagation()}
            />
          </div>
          <DropdownMenuSeparator />
          <DropdownMenuItem 
            onClick={() => handleAddLink('single')}
            disabled={!inputValue.trim()}
          >
            Parse Single Page
          </DropdownMenuItem>
          <DropdownMenuItem 
            onClick={() => handleAddLink('full')}
            disabled={!inputValue.trim()}
          >
            Parse Full Website
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
}