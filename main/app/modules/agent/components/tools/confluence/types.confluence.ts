export interface ConfluenceSpace {
  id: number;
  key: string;
  name: string;
  type: string;
  alias?: string;
  status?: string;
  _links?: {
    webui?: string;
    self?: string;
  };
}

export interface ConfluencePage {
  id: string;
  type: string;
  status: string;
  title: string;
  space: {
    id: number;
    key: string;
    name: string;
    type: string;
  };
  version: {
    when: string;
    by: {
      displayName: string;
    };
  };
  _links: {
    webui: string;
    self: string;
  };
}

export interface ListSpacesResponse {
  success: boolean;
  spaces?: ConfluenceSpace[];
  error?: string;
}

export interface ListPagesResponse {
  success: boolean;
  pages?: ConfluencePage[];
  error?: string;
}

export interface VectorSearchResult {
  score: number;
  payload: {
    source: 'confluence';
    page_id: string;
    title: string;
    space_key: string;
    space_name: string;
    modified_time: string;
    url?: string;
    content: string;
    type: string;
  };
}

export interface VectorSearchResponse {
  success: boolean;
  results?: VectorSearchResult[];
  error?: string;
}