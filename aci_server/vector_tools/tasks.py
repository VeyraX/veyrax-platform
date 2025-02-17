from celery_app import celery_app
from vector_tools.vector_tools import VectorStoreActions
from vector_tools.data_sources.google_drive import GoogleDriveSource
from integrations.google_drive.service import DriveService, DriveClient
from db.supabase import get_supabase
import os
from google.oauth2.credentials import Credentials
from vector_tools.data_sources.notion import NotionSource
from integrations.notion.service import NotionService
from integrations.notion.client import NotionClient
from fastapi import HTTPException
from datetime import datetime


def update_index_status(user_id: str, collection_name: str, status: str) -> None:
    try:
        supabase = get_supabase()
        
        result = supabase.table('users_provider_indexes') \
            .select('*') \
            .eq('user_id', user_id) \
            .eq('collection_name', collection_name) \
            .execute()
            
        if not result.data:
            raise HTTPException(status_code=404, detail="Index record not found")
            
        current_time = datetime.now().isoformat()
            
        supabase.table('users_provider_indexes') \
            .update({'status': status, 'last_sync_date': current_time}) \
            .eq('user_id', user_id) \
            .eq('collection_name', collection_name) \
            .execute()
            
    except Exception as e:
        print(f"Error updating index status: {str(e)}")
        supabase.table('users_provider_indexes') \
            .update({'status': 'failed'}) \
            .eq('user_id', user_id) \
            .eq('collection_name', collection_name) \
            .execute()
        raise

@celery_app.task(name="process_google_drive_documents")
def process_google_drive_documents_task(drive_service_credentials: dict, user_id: str):
    try:
        update_index_status(user_id, "google-drive", "syncing")
        
        creds = Credentials(
            token=drive_service_credentials['access_token'],
            refresh_token=drive_service_credentials['refresh_token'],
            token_uri="https://oauth2.googleapis.com/token",
            client_id=os.getenv('GOOGLE_CLIENT_ID'),
            client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
            scopes=drive_service_credentials['scopes'].split()
        )
        
        drive_client = DriveClient(credentials=creds)
        drive_service = DriveService(drive_client)
        
        google_drive_source = GoogleDriveSource(drive_service.client, user_id)
        
        vector_store = VectorStoreActions("google-drive")
        
        try:
            vector_store.get_collections("google-drive")
        except Exception:
            vector_store.create_collection("google-drive")
        
        vector_store.process_data_source(google_drive_source)
        
        update_index_status(user_id, "google-drive", "synced")
        
        return {
            "status": "success",
            "message": "Google Drive documents have been processed and vectorized"
        }
    except Exception as e:
        update_index_status(user_id, "google-drive", "failed")
        return {
            "status": "error",
            "message": str(e)
        }

@celery_app.task(name="process_notion_documents")
def process_notion_documents_task(auth_header: dict, user_id: str):
    try:
        update_index_status(user_id, "notion", "syncing")
        
        auth_token = auth_header.get('access_token')
        if not auth_token:
            raise ValueError("No access token provided")
        
        notion_client = NotionClient(auth_token=auth_token)
        notion_service = NotionService(notion_client)
        notion_source = NotionSource(notion_service, user_id)
        
        vector_store = VectorStoreActions("notion")
        
        try:
            vector_store.get_collections("notion")
        except Exception:
            vector_store.create_collection("notion")
        
        vector_store.process_data_source(notion_source)
        
        update_index_status(user_id, "notion", "synced")
        
        return {
            "status": "success",
            "message": "Notion documents have been processed and vectorized"
        }
    except Exception as e:
        update_index_status(user_id, "notion", "failed")
        return {
            "status": "error",
            "message": str(e)
        }