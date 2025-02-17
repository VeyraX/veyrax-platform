import React from 'react';
import { VectorSearchResponse } from './types.notion';
import { ToolCard, ToolCardSkeleton } from "../common/tool-card"

interface Props {
  response: VectorSearchResponse;
}

export const NotionResponseView: React.FC<Props> = ({ response }) => {
  if (!response.success || !response.results?.length) {
    return null;
  }

  return (
    <>
      {response.results.map((result, index) => (
        <ToolCard
          key={index}
          resourceType="notion/page"
          title={result.payload.title}
          subtitle={`Relevance: ${result.score.toFixed(2)}`}
          externalLink={result.payload.url}
        />
      ))}
    </>
  );
};

export const NotionResponseSkeleton: React.FC = () => {
  return <ToolCardSkeleton />;
};