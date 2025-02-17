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
  
export interface VectorSearchResult {
  score: number;
  payload: {
    source: 'notion';
    doc_id: string;
    title: string;
    database_id: string;
    url: string;
    last_edited_time: string;
    user_id: string;
    content: string;
    part?: number;
    total_parts?: number;
  };
}

export interface VectorSearchResponse {
  success: boolean;
  results?: VectorSearchResult[];
  error?: string;
}
  