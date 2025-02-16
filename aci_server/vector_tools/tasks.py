from celery_app import celery_app
from vector_tools.vector_tools import VectorStoreActions
from vector_tools.data_sources.google_drive import GoogleDriveSource
from integrations.google_drive.service import DriveService, DriveClient
import os
from google.oauth2.credentials import Credentials
from vector_tools.data_sources.notion import NotionSource
from integrations.notion.service import NotionService
from integrations.notion.client import NotionClient


@celery_app.task(name="process_google_drive_documents")
def process_google_drive_documents_task(drive_service_credentials: dict):
    try:
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
        
        google_drive_source = GoogleDriveSource(drive_service.client)
        
        vector_store = VectorStoreActions("google-drive")
        
        try:
            vector_store.get_collections("google-drive")
        except Exception:
            vector_store.create_collection("google-drive")
        
        vector_store.process_data_source(google_drive_source)
        
        return {
            "status": "success",
            "message": "Google Drive documents have been processed and vectorized"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@celery_app.task(name="process_notion_documents")
def process_notion_documents_task(auth_header: str):
    try:
        # Extract the token from the auth header
        auth_token = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else auth_header
        
        notion_client = NotionClient(auth_token=auth_token)
        notion_service = NotionService(notion_client)
        notion_source = NotionSource(notion_service)
        
        vector_store = VectorStoreActions("notion")
        
        try:
            vector_store.get_collections("notion")
        except Exception:
            vector_store.create_collection("notion")
        
        vector_store.process_data_source(notion_source)
        
        return {
            "status": "success",
            "message": "Notion documents have been processed and vectorized"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }