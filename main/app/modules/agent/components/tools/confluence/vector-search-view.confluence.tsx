import React from 'react';
import { VectorSearchResponse } from './types.confluence';
import { ToolCard, ToolCardSkeleton } from "../common/tool-card"

interface Props {
  response: VectorSearchResponse;
}

export const ConfluenceResponseView: React.FC<Props> = ({ response }) => {
  
  if (!response.success || !response.results?.length) {
    return null;
  }

  return (
    <>
      {response.results.map((result, index) => {
        return (
          <ToolCard
            key={index}
            resourceType={`confluence/${result.payload.source}`}
            title={result.payload.title}
            subtitle={`${result.payload.space_name} • Relevance: ${result.score.toFixed(2)}`}
            externalLink={result.payload.url}
          />
        );
      })}
    </>
  );
};

export const ConfluenceResponseSkeleton: React.FC = () => {
  return <ToolCardSkeleton />;
};