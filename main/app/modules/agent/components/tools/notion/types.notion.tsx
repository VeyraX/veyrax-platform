export type Database = {
    id: string
    title: string
    last_edited_time: string
}

export type Page = {
    title: string
    created_time: string
    last_edited_time: string
    archived: boolean
    url: string
    content: any[]
  }
  
export type PageList = {
    items: Page[]
  }
  