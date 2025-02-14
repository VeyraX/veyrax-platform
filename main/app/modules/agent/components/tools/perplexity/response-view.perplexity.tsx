import React from 'react';
import { PerplexityResponse } from './types.perplexity';
import { Card, CardContent } from "@/components/ui/card";
import { ExternalLink } from "lucide-react";
import ReactMarkdown from 'react-markdown';
import { Skeleton } from "@/components/ui/skeleton";

interface Props {
  response: PerplexityResponse;
}

export const PerplexityResponseView: React.FC<Props> = ({ response }) => {
  const content = response.choices[0]?.message.content;
  const citations = response.citations;

  return (
    <div className="flex flex-col gap-4">
      {/* Main content with markdown */}
      <div className="prose max-w-none">
        <ReactMarkdown
          components={{
            p: ({node, ...props}) => <p className="my-2" {...props}/>,
            ul: ({node, ...props}) => <ul className="pl-4 my-2 list-disc" {...props}/>,
            ol: ({node, ...props}) => <ol className="pl-4 my-2 list-decimal" {...props}/>,
            li: ({node, ...props}) => <li className="my-1" {...props}/>,
            h1: ({node, ...props}) => <h1 className="text-2xl font-bold my-4" {...props}/>,
            h2: ({node, ...props}) => <h2 className="text-xl font-semibold my-3" {...props}/>,
            h3: ({node, ...props}) => <h3 className="text-lg font-medium my-2" {...props}/>,
          }}
        >
          {content}
        </ReactMarkdown>
      </div>

      {/* Citations as cards */}
      {citations && citations.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {citations.map((citation, index) => (
            <Card key={index} className="w-[250px]">
              <CardContent className="p-2 flex flex-col">
                <div className="flex items-center justify-between gap-2">
                  <span className="truncate text-xs font-medium">
                    {new URL(citation).hostname}
                  </span>
                  <a
                    href={citation}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-muted-foreground hover:text-foreground"
                  >
                    <ExternalLink className="h-3 w-3 flex-shrink-0" />
                  </a>
                </div>
                <a
                  href={citation}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-[10px] text-muted-foreground hover:underline truncate"
                >
                  {citation}
                </a>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export const PerplexityResponseSkeleton: React.FC = () => {
  return (
    <div className="flex flex-col gap-4">
      <div className="space-y-2">
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-[90%]" />
        <Skeleton className="h-4 w-[95%]" />
        <Skeleton className="h-4 w-[85%]" />
        <Skeleton className="h-4 w-[70%]" />
      </div>
    </div>
  );
};