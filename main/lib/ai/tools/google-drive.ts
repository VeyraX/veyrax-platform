import { tool } from 'ai';
import { z } from 'zod';
import { getAuthHeaders } from '@/lib/actions/actions';
import * as pdfjs from 'pdfjs-dist';

export const googleDrive_listFiles = tool({
  description: 'List files in Google Drive with optional filters',
  parameters: z.object({
    nameContains: z.string().optional().describe('Filter files by name containing this string'),
    mimeType: z.string().optional().describe('Filter files by MIME type'),
    parentId: z.string().optional().describe('Filter files by parent folder ID'),
    createdAfter: z.string().optional().describe('Filter files created after date (YYYY-MM-DD)'),
    createdBefore: z.string().optional().describe('Filter files created before date (YYYY-MM-DD)'),
    pageToken: z.string().optional().describe('Page token for pagination'),
  }),
  execute: async function({ nameContains, mimeType, parentId, createdAfter, createdBefore, pageToken }) {
    try {
      const headers = await getAuthHeaders();
      const params = new URLSearchParams();
      if (nameContains) params.append('name_contains', nameContains);
      if (mimeType) params.append('mime_type', mimeType);
      if (parentId) params.append('parent_id', parentId);
      if (createdAfter) params.append('created_after', createdAfter);
      if (createdBefore) params.append('created_before', createdBefore);
      if (pageToken) params.append('page_token', pageToken);

      const response = await fetch(`http://localhost:8000/google_drive/files?${params.toString()}`, {
        headers,
        credentials: 'include'
      });
      if (!response.ok) throw new Error('Failed to list files');
      
      const data = await response.json();
      return {
        success: true,
        files: data.files,
        pageToken: data.page_token
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to list files'
      };
    }
  }
});

export const googleDrive_listFolders = tool({
  description: 'List folders in Google Drive',
  parameters: z.object({
    nameContains: z.string().optional().describe('Filter folders by name containing this string'),
    parentId: z.string().optional().describe('Filter folders by parent folder ID'),
    pageToken: z.string().optional().describe('Page token for pagination'),
  }),
  execute: async function({ nameContains, parentId, pageToken }) {
    try {
      const headers = await getAuthHeaders();
      const params = new URLSearchParams();
      if (nameContains) params.append('name_contains', nameContains);
      if (parentId) params.append('parent_id', parentId);
      if (pageToken) params.append('page_token', pageToken);

      const response = await fetch(`http://localhost:8000/google_drive/folders?${params.toString()}`, {
        headers,
        credentials: 'include'
      });
      if (!response.ok) throw new Error('Failed to list folders');
      
      const data = await response.json();
      return {
        success: true,
        folders: data.files,
        pageToken: data.page_token
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to list folders'
      };
    }
  }
});


export const googleDrive_getFile = tool({
  description: 'Get file metadata from Google Drive',
  parameters: z.object({
    fileId: z.string().describe('ID of the file to get information about'),
  }),
  execute: async function({ fileId }) {
    try {
      const headers = await getAuthHeaders();
      const response = await fetch(`http://localhost:8000/google_drive/files/${fileId}`, {
        headers,
        credentials: 'include'
      });
      if (!response.ok) throw new Error('Failed to get file information');
      
      const data = await response.json();
      return {
        success: true,
        file: data
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to get file information'
      };
    }
  }
});

export const googleDrive_moveFile = tool({
  description: 'Move a file to a different folder in Google Drive',
  parameters: z.object({
    fileId: z.string().describe('ID of the file to move'),
    newParentId: z.string().describe('ID of the destination folder'),
  }),
  execute: async function({ fileId, newParentId }) {
    try {
      const headers = await getAuthHeaders();
      const response = await fetch(`http://localhost:8000/google_drive/files/${fileId}/move`, {
        method: 'PATCH',
        headers: {
          ...headers,
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ new_parent_id: newParentId }),
      });

      if (!response.ok) throw new Error('Failed to move file');
      
      const data = await response.json();
      return {
        success: true,
        file: data
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to move file'
      };
    }
  }
});

export const googleDrive_readFile = tool({
  description: 'Read content from a file in Google Drive (supports text files, PDFs, DOC, etc. but not spreadsheets)',
  parameters: z.object({
    fileId: z.string().describe('ID of the file to read'),
  }),
  execute: async function({ fileId }) {
    try {
      const headers = await getAuthHeaders();
      const response = await fetch(`http://localhost:8000/google_drive/files/${fileId}/read`, {
        headers,
        credentials: 'include'
      });
      if (!response.ok) throw new Error('Failed to read file');
      
      const data = await response.json();
      return {
        success: data.success,
        content: data.content,
        file: data.file,
        mime_type: data.mime_type,
        error: data.error
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to read file'
      };
    }
  }
});