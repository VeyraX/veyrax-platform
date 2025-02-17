export interface DriveFile {
    id: string;
    name: string;
    mime_type: string;
    parent_ids?: string[];
    parent_names?: string[];
    created_time: string;
    modified_time: string;
    size?: number;
    web_view_link?: string;
    web_content_link?: string;
  }
  
  export interface FileList {
    files: DriveFile[];
    page_token?: string;
  }
  
  export interface FileFilters {
    name_contains?: string;
    mime_type?: string;
    parent_id?: string;
    created_after?: string;
    created_before?: string;
  }
  
  export interface FileUpload {
    name: string;
    parent_id?: string;
    mime_type: string;
  }
  
  export interface FolderCreate {
    name: string;
    parent_id?: string;
  }
  
  export interface FileMove {
    new_parent_id: string;
  }
  
  export interface ListFilesResponse {
    success: boolean;
    files?: DriveFile[];
    pageToken?: string;
    error?: string;
  }
  
  export interface ListFoldersResponse {
    success: boolean;
    folders?: DriveFile[];
    pageToken?: string;
    error?: string;
  }
  
  export interface ReadFileResponse {
    success: boolean;
    content?: string;
    file?: DriveFile;
    mime_type?: string;
    error?: string;
  }
  
  export interface GetFileResponse {
    success: boolean;
    file?: DriveFile;
    error?: string;
  }
  
  export interface MoveFileResponse {
    success: boolean;
    file?: DriveFile;
    error?: string;
  }
  
  export interface VectorSearchResult {
    score: number;
    payload: {
      source: 'google_drive';
      doc_id: string;
      title: string;
      modified_time: string;
      web_view_link?: string;
      parent_ids?: string[];
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