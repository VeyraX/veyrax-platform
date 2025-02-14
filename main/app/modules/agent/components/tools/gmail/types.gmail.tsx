
export interface MessageProps {
    subject: string
    snippet: string
    body: string
    sender: string
    recipient: string
    labels: string[]
    date: string
  }


export interface DraftMessageProps {
    to: string
    subject: string
    body: string
  }