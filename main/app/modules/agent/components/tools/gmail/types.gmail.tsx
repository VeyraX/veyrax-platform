export interface MessageProps {
    id: string
    thread_id: string
    subject: string
    snippet: string
    body: string
    sender: string
    recipient: string
    date: string
    html_link: string
    labels?: string[]
}


export interface DraftMessageProps {
    to: string
    subject: string
    body: string
  }