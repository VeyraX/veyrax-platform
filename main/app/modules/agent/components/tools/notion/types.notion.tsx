export type Database = {
    id: string
    title: string
    last_edited_time: string
}

export type Page = {
    id?: string;
    title?: string;
    created_time?: string;
    last_edited_time?: string;
    archived?: boolean;
    url?: string;
    content?: any[];
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

export type DatabaseProperty = {
  id: string;
  name: string;
  type: string;
  // Specific property configurations based on type
  [key: string]: any;
}

export type DatabaseWithProperties = {
  id: string;
  title: string;
  properties: Record<string, DatabaseProperty>;
}

export type DatabaseQuerySort = {
  property?: string;
  timestamp?: 'created_time' | 'last_edited_time';
  direction: 'ascending' | 'descending';
}

export type DatabaseQueryFilter = {
  property?: string;
  [key: string]: any;
}

export type DatabaseQueryResponse = {
  items: Page[];
  next_cursor?: string;
}

export type PageUpdate = {
  pageId: string;
  title?: string;
  properties?: Record<string, any>;
  content?: Record<string, any>;
}
  