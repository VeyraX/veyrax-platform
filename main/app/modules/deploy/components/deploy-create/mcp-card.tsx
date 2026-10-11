import React from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { ExternalMcpRepository } from '../../api/types.deploy';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ArrowUpRight } from 'lucide-react';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

interface McpCardProps {
  repository: ExternalMcpRepository;
  onSelect?: (repoUrl: string) => void;
}

export function McpCardSkeleton() {
  return (
    <Card className="h-full flex flex-col shadow-none border border-muted">
      <CardHeader className="p-4 pb-2">
        <div className="flex items-start justify-between">
          <div className="w-2/3 h-5 bg-muted rounded animate-pulse" />
          <div className="h-6 w-6 rounded-full bg-muted animate-pulse" />
        </div>
        <div className="flex items-center gap-1.5 w-fit mt-2">
          <div className="w-3 h-3 bg-muted rounded-full animate-pulse" />
          <div className="w-24 h-3 bg-muted rounded animate-pulse" />
        </div>
      </CardHeader>
      <CardContent className="p-4 pt-2 flex-grow">
        <div className="space-y-1.5">
          <div className="w-full h-3 bg-muted rounded animate-pulse" />
          <div className="w-3/4 h-3 bg-muted rounded animate-pulse" />
        </div>
      </CardContent>
    </Card>
  );
}

export function McpCard({ repository, onSelect }: McpCardProps) {
  const { name, metadata } = repository;
  const { 
    source_code_url,
    short_description
  } = metadata || {};

  const handleSelect = () => {
    if (source_code_url && onSelect) {
      onSelect(source_code_url);
    }
  };

  // Truncate the description to 50 characters
  const truncatedDescription = short_description 
    ? short_description.length > 50 
      ? `${short_description.substring(0, 50)}...` 
      : short_description
    : 'No description available';

  return (
    <Card 
      className="h-full flex flex-col shadow-none group relative cursor-pointer"
      onClick={source_code_url && onSelect ? handleSelect : undefined}
    >
      <CardHeader className="p-4 pb-2">
        <div className="flex items-start justify-between">
          <CardTitle className="text-base font-medium truncate mr-2">{name}</CardTitle>
          {onSelect && source_code_url && (
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button 
                    size="icon" 
                    variant="ghost" 
                    className="h-6 w-6 p-0 group-hover:translate-x-1 group-hover:-translate-y-1 transition-transform"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleSelect();
                    }}
                  >
                    <ArrowUpRight size={14} />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>
                  <p>Deploy this MCP</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          )}
        </div>
        {source_code_url && (
          <Link
            href={source_code_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs text-muted-foreground hover:text-primary flex items-center gap-1.5 w-fit mt-1"
            onClick={(e) => e.stopPropagation()}
          >
            <Image
              src="https://zpjxdtvecaxrdxvfaxom.supabase.co/storage/v1/object/public/logos//github-logo.svg"
              alt="GitHub"
              width={12}
              height={12}
            />
            <span className="truncate max-w-[200px]">
              {new URL(source_code_url).pathname.split('/').slice(-2).join('/')}
            </span>
          </Link>
        )}
      </CardHeader>
      <CardContent className="p-4 pt-2 flex-grow">
        <CardDescription className="text-xs">
          {truncatedDescription}
        </CardDescription>
      </CardContent>
    </Card>
  );
}
