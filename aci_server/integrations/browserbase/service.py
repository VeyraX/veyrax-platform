import os
from typing import Dict, Any, Optional, List
from .client import BrowserBaseClient
from .schema import (
    SessionDetails,
    SessionList,
    ContextDetails,
    SessionDebugDetails,
    LogEntryList,
    RecordingEntryList,
    ApiResponse,
    PageList,
    PageDetails,
    ProjectDetails,
    ProjectList,
    ProjectUsage,
    ExtensionDetails
)
from ..common.component_handler import load_components, prepare_components_auto

class BrowserBaseService:
    def __init__(self, client: BrowserBaseClient):
        self.client = client
        self.components_data = self._load_components()
        
    def _load_components(self) -> Dict[str, Any]:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)
    
    def prepare_response(self, data: Any, component_name: str = None) -> ApiResponse:
        tool_name = "browser-base"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)
    
    def get_session(self, session_id: str) -> ApiResponse:
        """Get details about a specific session"""
        response = self.client.get_session(session_id)
        session_details = SessionDetails(**response)
        return self.prepare_response(session_details, "BrowserBaseSessionDetail")
    
    def create_session(self, params: Dict[str, Any]) -> ApiResponse:
        """Create a new browser session"""
        response = self.client.create_session(params)
        session_details = SessionDetails(**response)
        return self.prepare_response(session_details, "BrowserBaseSessionDetail")
    
    def update_session(self, session_id: str, update_params: Dict[str, Any]) -> ApiResponse:
        """Update a session's status"""
        response = self.client.update_session(session_id, update_params)
        session_details = SessionDetails(**response)
        return self.prepare_response(session_details, "BrowserBaseSessionDetail")
    
    def list_sessions(self, params: Optional[Dict[str, Any]] = None) -> ApiResponse:
        """List all sessions with optional filtering"""
        response = self.client.list_sessions(params)
        sessions = [SessionDetails(**session) for session in response]
        session_list = SessionList(items=sessions)
        return self.prepare_response(session_list, "BrowserBaseSessionList")
    
    def get_context(self, context_id: str) -> ApiResponse:
        """Get details about a specific context"""
        response = self.client.get_context(context_id)
        context_details = ContextDetails(**response)
        return self.prepare_response(context_details, "BrowserBaseContextDetail")
    
    def create_context(self, params: Dict[str, Any]) -> ApiResponse:
        """Create a new browser context"""
        response = self.client.create_context(params)
        context_details = ContextDetails(**response)
        return self.prepare_response(context_details, "BrowserBaseContextDetail")
    
    def delete_context(self, context_id: str) -> Dict[str, Any]:
        """Delete a browser context"""
        self.client.delete_context(context_id)
        return {"status_code": 204, "message": "Context deleted successfully"}
    
    def get_session_logs(self, session_id: str) -> ApiResponse:
        """Get logs for a specific session"""
        response = self.client.get_session_logs(session_id)
        
        if isinstance(response, list):
            raw_entries = response
        elif isinstance(response, dict) and 'data' in response and isinstance(response['data'], list):
            raw_entries = response['data']
        else:
            raw_entries = []
        
        log_entries = []
        for entry in raw_entries:
            try:
                processed_entry = self._process_log_entry(entry)
                log_entries.append(processed_entry)
            except Exception as e:
                print(f"Error processing log entry: {e}")
                continue
        
        log_entry_list = LogEntryList(items=log_entries)
        return self.prepare_response(log_entry_list, "BrowserBaseLogsList")
    
    def _process_log_entry(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """Process log entry for proper structure"""
        processed_entry = {}
        
        processed_entry["method"] = str(entry.get("method", ""))
        processed_entry["pageId"] = int(entry.get("pageId", 0))
        processed_entry["sessionId"] = str(entry.get("sessionId", ""))
        processed_entry["timestamp"] = int(entry.get("timestamp", 0))
        processed_entry["frameId"] = str(entry.get("frameId", ""))
        processed_entry["loaderId"] = str(entry.get("loaderId", ""))
        
        request = entry.get("request", {})
        if not isinstance(request, dict):
            request = {}
        
        processed_entry["request"] = {
            "timestamp": int(request.get("timestamp", 0)),
            "params": request.get("params", {}),
            "rawBody": str(request.get("rawBody", ""))
        }
        
        response = entry.get("response", {})
        if not isinstance(response, dict):
            response = {}
        
        processed_entry["response"] = {
            "timestamp": int(response.get("timestamp", 0)),
            "result": response.get("result", {}),
            "rawBody": str(response.get("rawBody", ""))
        }
        
        return processed_entry
    
    def get_session_recording(self, session_id: str) -> ApiResponse:
        """Get recording data for a specific session"""
        response = self.client.get_session_recording(session_id)
        recording_entries = [self._process_recording_entry(entry) for entry in response]
        recording_entry_list = RecordingEntryList(items=recording_entries)
        return self.prepare_response(recording_entry_list, "BrowserBaseRecordingList")
    
    def _process_recording_entry(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """Process recording entry for proper structure"""
        if "data" not in entry:
            entry["data"] = {}
        return entry
    
    def get_session_debug(self, session_id: str) -> ApiResponse:
        """Get debug information for a specific session"""
        response = self.client.get_session_debug(session_id)
        
        # Process pages to create PageList
        if "pages" in response and isinstance(response["pages"], list):
            pages = [PageDetails(**page) for page in response["pages"]]
            response["pages"] = PageList(items=pages)
            
        debug_details = SessionDebugDetails(**response)
        return self.prepare_response(debug_details, "BrowserBaseDebugInfo")
    
    def get_session_downloads(self, session_id: str) -> Dict[str, Any]:
        """Download data from a specific session"""
        response = self.client.get_session_downloads(session_id)
        return response
    
    def create_session_uploads(self, session_id: str, file_content: str) -> ApiResponse:
        """Upload a file to a specific session"""
        response = self.client.create_session_uploads(session_id, file_content)
        return self.prepare_response(response, "BrowserBaseUploadResult")
    
    def validate_key(self, api_key: str) -> Dict[str, Any]:
        """Test if the API key is valid"""
        try:
            client = BrowserBaseClient(api_key=api_key)
            is_valid = client.test_connection()
            if is_valid:
                return {"valid": True, "message": "API key is valid"}
            else:
                return {"valid": False, "message": "Invalid API key"}
        except Exception as e:
            return {"valid": False, "message": f"Error validating API key: {str(e)}"}
    
    def list_projects(self) -> ApiResponse:
        """List all projects for the authenticated user"""
        response = self.client.list_projects()
        projects = [ProjectDetails(**project) for project in response]
        project_list = ProjectList(items=projects)
        return self.prepare_response(project_list, "BrowserBaseProjectList")
    
    def get_project(self, project_id: str) -> ApiResponse:
        """Get details about a specific project"""
        response = self.client.get_project(project_id)
        project_details = ProjectDetails(**response)
        return self.prepare_response(project_details, "BrowserBaseProjectDetail")
    
    def get_project_usage(self, project_id: str) -> ApiResponse:
        """Get usage statistics for a specific project"""
        response = self.client.get_project_usage(project_id)
        project_usage = ProjectUsage(**response)
        return self.prepare_response(project_usage, "BrowserBaseProjectUsage")
    
    def get_extension(self, extension_id: str) -> ApiResponse:
        """Get details about a specific extension"""
        response = self.client.get_extension(extension_id)
        extension_details = ExtensionDetails(**response)
        return self.prepare_response(extension_details, "BrowserBaseExtensionDetail")
    
    def delete_extension(self, extension_id: str) -> Dict[str, Any]:
        """Delete an extension"""
        self.client.delete_extension(extension_id)
        return {"status_code": 204, "message": "Extension deleted successfully"}
    
    def upload_extension(self, file_content: str, project_id: Optional[str] = None) -> ApiResponse:
        """Upload an extension"""
        response = self.client.upload_extension(file_content, project_id)
        extension_details = ExtensionDetails(**response)
        return self.prepare_response(extension_details, "BrowserBaseExtensionDetail")
