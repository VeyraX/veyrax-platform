import React from 'react';
import { VectorSearchResponse } from './types.google-drive';
import { Card, CardContent } from "@/components/ui/card";
import { ExternalLink } from "lucide-react";
import ReactMarkdown from 'react-markdown';
import { Skeleton } from "@/components/ui/skeleton";
import { ToolCard, ToolCardSkeleton } from "../common/tool-card"

interface Props {
  response: VectorSearchResponse;
}

export const GoogleDriveResponseView: React.FC<Props> = ({ response }) => {
  if (!response.success || !response.results?.length) {
    return null;
  }

  return (
    <>
      {response.results.map((result, index) => (
        <ToolCard
          key={index}
          resourceType="google-drive/file"
          title={result.payload.title}
          subtitle={`Relevance: ${result.score.toFixed(2)}`}
          externalLink={result.payload.web_view_link}
        />
      ))}
    </>
  );
};

export const GoogleDriveResponseSkeleton: React.FC = () => {
  return <ToolCardSkeleton />;
};