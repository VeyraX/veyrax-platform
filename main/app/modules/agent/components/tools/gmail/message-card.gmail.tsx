import { MessageProps } from "./types.gmail"
import { ToolCard, ToolCardSkeleton } from "../common/tool-card"

export function MessageCard({ message }: { message: MessageProps  }) {
  return (
    <ToolCard
      resourceType="gmail/message"
      title={message.subject || 'No Subject'}
      subtitle={`To: ${message.recipient || 'No Recipient'}`}
      externalLink={message.html_link}
    />
  )
}

export function MessageCardSkeleton() {
  return <ToolCardSkeleton />
}