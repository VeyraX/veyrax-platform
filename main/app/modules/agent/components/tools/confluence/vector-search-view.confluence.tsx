import React from 'react';
import { VectorSearchResponse } from './types.confluence';
import { ToolCard, ToolCardSkeleton } from "../common/tool-card"

interface Props {
  response: VectorSearchResponse;
}

export const ConfluenceResponseView: React.FC<Props> = ({ response }) => {
  console.log('Confluence Vector Search Response:', response);
  
  if (!response.success || !response.results?.length) {
    return null;
  }

  const baseUrl = "https://korzhovwork2019.atlassian.net/wiki";

  return (
    <>
      {response.results.map((result, index) => {
        console.log('Result item:', result);
        console.log('Result payload:', result.payload);
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