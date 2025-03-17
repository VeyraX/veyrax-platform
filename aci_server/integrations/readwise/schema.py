from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum

class DocumentLocation(str, Enum):
    NEW = "new"
    LATER = "later"
    ARCHIVE = "archive"
    FEED = "feed"
    SHORTLIST = "shortlist"

class DocumentCategory(str, Enum):
    ARTICLE = "article"
    EMAIL = "email"
    RSS = "rss"
    HIGHLIGHT = "highlight"
    NOTE = "note"
    PDF = "pdf"
    EPUB = "epub"
    TWEET = "tweet"
    VIDEO = "video"

# Input schemas
class SaveDocumentParams(BaseModel):
    url: str = Field(..., description="The document's unique URL")
    html: Optional[str] = Field(None, description="The document's content in valid HTML")
    should_clean_html: Optional[bool] = Field(None, description="Whether to clean the HTML and parse metadata")
    title: Optional[str] = Field(None, description="The document's title")
    author: Optional[str] = Field(None, description="The document's author")
    summary: Optional[str] = Field(None, description="Summary of the document")
    published_date: Optional[str] = Field(None, description="Publication date in ISO 8601 format")
    image_url: Optional[str] = Field(None, description="URL for cover image")
    location: Optional[DocumentLocation] = Field(None, description="Initial location of the document")
    category: Optional[DocumentCategory] = Field(None, description="Category of the document")
    saved_using: Optional[str] = Field(None, description="Source of the document")
    tags: Optional[List[str]] = Field(None, description="List of tags")
    notes: Optional[str] = Field(None, description="Top-level note of the document")

class ListDocumentsParams(BaseModel):
    id: Optional[str] = Field(None, description="Document's unique ID")
    updatedAfter: Optional[str] = Field(None, description="Fetch documents updated after this date (ISO 8601)")
    location: Optional[DocumentLocation] = Field(None, description="Document's location")
    category: Optional[DocumentCategory] = Field(None, description="Document's category")
    pageCursor: Optional[str] = Field(None, description="Cursor for pagination")
    withHtmlContent: Optional[bool] = Field(None, description="Include HTML content in response")

class UpdateDocumentParams(BaseModel):
    title: Optional[str] = Field(None, description="The document's title")
    author: Optional[str] = Field(None, description="The document's author")
    summary: Optional[str] = Field(None, description="Summary of the document")
    published_date: Optional[str] = Field(None, description="Publication date in ISO 8601 format")
    image_url: Optional[str] = Field(None, description="URL for cover image")
    location: Optional[DocumentLocation] = Field(None, description="Location of the document")
    category: Optional[DocumentCategory] = Field(None, description="Category of the document")

class DeleteDocumentParams(BaseModel):
    document_id: str = Field(..., description="ID of the document to delete")

class DocumentResponse(BaseModel):
    id: str
    url: str

class Document(BaseModel):
    id: str
    url: str
    source_url: Optional[str] = None
    title: Optional[str] = None
    author: Optional[str] = None
    source: Optional[str] = None
    category: Optional[str] = None
    location: Optional[str] = None
    tags: Optional[Dict[str, Any]] = None
    site_name: Optional[str] = None
    word_count: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    notes: Optional[str] = None
    published_date: Optional[str] = None
    summary: Optional[str] = None
    image_url: Optional[str] = None
    parent_id: Optional[str] = None
    reading_progress: Optional[float] = None
    first_opened_at: Optional[str] = None
    last_opened_at: Optional[str] = None
    saved_at: Optional[str] = None
    last_moved_at: Optional[str] = None
    html_content: Optional[str] = None
    
    class Config:
        extra = 'allow'

class DocumentListResponse(BaseModel):
    count: int
    nextPageCursor: Optional[str] = None
    results: List[Document]
    
    class Config:
        extra = 'allow'

class ApiResponse(BaseModel):
    data: Union[DocumentResponse, DocumentListResponse, Document]
    component: Optional[Dict[str, Any]] = None