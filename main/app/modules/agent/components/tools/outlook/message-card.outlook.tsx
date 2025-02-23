import { MessageProps } from "./types.outlook"
import { ToolCard, ToolCardSkeleton } from "../common/tool-card"

export function MessageCard({ message }: { message: MessageProps }) {
  return (
    <ToolCard
      resourceType="outlook/message"
      title={message.subject || 'No Subject'}
      subtitle={`To: ${Array.isArray(message.to) ? message.to.join(', ') : 'No Recipient'}`}
      externalLink={message.webLink}
    />
  )
}

export function MessageCardSkeleton() {
  return <ToolCardSkeleton />
}