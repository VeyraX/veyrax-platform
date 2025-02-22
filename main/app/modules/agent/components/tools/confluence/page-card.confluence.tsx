import { ToolCard } from "../common/tool-card"
import { ConfluencePage, ConfluenceSpace } from "./types.confluence"
import { formatDistanceToNow } from "date-fns"

interface PageCardProps {
  page: ConfluencePage | ConfluenceSpace;
}

export function PageCard({ page }: PageCardProps) {
  console.log('PageCard received page:', page);

  const isSpace = 'key' in page && !('space' in page);

  if (isSpace) {
    const space = page as ConfluenceSpace;
    return (
      <ToolCard
        resourceType={`confluence/space`}
        title={space.name}
        subtitle={`${space.key} • ${space.type}`}
        externalLink={space._links?.webui}
      />
    );
  }

  const confluencePage = page as ConfluencePage;
  const formattedDate = confluencePage.version?.when 
    ? formatDistanceToNow(new Date(confluencePage.version.when), { addSuffix: true })
    : 'No date';

  const spaceName = confluencePage.space?.name || 'Unknown Space';

  return (
    <ToolCard
      resourceType={`confluence/${confluencePage.type}`}
      title={confluencePage.title}
      subtitle={`${spaceName} • ${formattedDate}`}
      externalLink={confluencePage._links?.webui}
    />
  );
}

export { ToolCardSkeleton as PageCardSkeleton } from "../common/tool-card"