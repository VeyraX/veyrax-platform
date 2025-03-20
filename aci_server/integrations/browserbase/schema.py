from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Union, Literal

# Common Models
class BrowserConfig(BaseModel):
    name: str
    version: str

class ViewportConfig(BaseModel):
    width: int
    height: int

class ScreenConfig(BaseModel):
    maxHeight: Optional[int] = None
    maxWidth: Optional[int] = None
    minHeight: Optional[int] = None
    minWidth: Optional[int] = None

class FingerprintConfig(BaseModel):
    httpVersion: Optional[str] = None
    browsers: Optional[List[str]] = None
    devices: Optional[List[str]] = None
    locales: Optional[List[str]] = None
    operatingSystems: Optional[List[str]] = None
    screen: Optional[ScreenConfig] = None

class ContextConfig(BaseModel):
    id: Optional[str] = None
    persist: Optional[bool] = None

class BrowserSettings(BaseModel):
    context: Optional[ContextConfig] = None
    extensionId: Optional[str] = None
    fingerprint: Optional[FingerprintConfig] = None
    viewport: Optional[ViewportConfig] = None
    blockAds: Optional[bool] = None
    solveCaptchas: Optional[bool] = None
    recordSession: Optional[bool] = None
    logSession: Optional[bool] = None
    advancedStealth: Optional[bool] = None

class Configuration(BaseModel):
    resolution: str
    timezone: str
    language: str

class Links(BaseModel):
    websocket: str
    screenshot: str

# Input Parameter Models
class GetSessionParams(BaseModel):
    id: str

class CreateSessionParams(BaseModel):
    projectId: str
    extensionId: Optional[str] = None
    browserSettings: Optional[BrowserSettings] = None
    timeout: Optional[int] = None
    keepAlive: Optional[bool] = None
    proxies: Optional[bool] = None
    region: Optional[str] = None
    userMetadata: Optional[Dict[str, Any]] = None

class UpdateSessionParams(BaseModel):
    id: str
    projectId: Optional[str] = None
    status: Optional[str] = None

class ListSessionsParams(BaseModel):
    status: Optional[str] = None
    q: Optional[str] = None

class GetContextParams(BaseModel):
    id: str

class CreateContextParams(BaseModel):
    projectId: str

class DeleteContextParams(BaseModel):
    id: str

class SessionLogsParams(BaseModel):
    id: str

class SessionRecordingParams(BaseModel):
    id: str

class SessionDebugParams(BaseModel):
    id: str

class SessionDownloadsParams(BaseModel):
    id: str

class SessionUploadsParams(BaseModel):
    id: str
    file: str

class ValidateApiKeyParams(BaseModel):
    api_key: str

# Input Parameter Models for Projects
class ListProjectsParams(BaseModel):
    pass  # No required parameters

class GetProjectParams(BaseModel):
    id: str

class GetProjectUsageParams(BaseModel):
    id: str

# Input Parameter Models for Extensions
class GetExtensionParams(BaseModel):
    id: str

class DeleteExtensionParams(BaseModel):
    id: str

class UploadExtensionParams(BaseModel):
    file: str
    projectId: Optional[str] = None

# Response Models
class SessionDetails(BaseModel):
    id: str
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None
    projectId: Optional[str] = None
    startedAt: Optional[str] = None
    endedAt: Optional[str] = None
    expiresAt: Optional[str] = None
    status: str
    proxyBytes: Optional[int] = None
    avgCpuUsage: Optional[int] = None
    memoryUsage: Optional[int] = None
    keepAlive: Optional[bool] = None
    contextId: Optional[str] = None
    region: Optional[str] = None
    userMetadata: Optional[Dict[str, Any]] = None
    connectUrl: Optional[str] = None
    seleniumRemoteUrl: Optional[str] = None
    signingKey: Optional[str] = None

class SessionList(BaseModel):
    items: List[SessionDetails]

class ContextDetails(BaseModel):
    id: str
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None
    projectId: Optional[str] = None
    uploadUrl: Optional[str] = None
    publicKey: Optional[str] = None
    cipherAlgorithm: Optional[str] = None
    initializationVectorSize: Optional[int] = None

class PageDetails(BaseModel):
    id: str
    url: str
    faviconUrl: Optional[str] = None
    title: Optional[str] = None
    debuggerUrl: Optional[str] = None
    debuggerFullscreenUrl: Optional[str] = None

class PageList(BaseModel):
    items: List[PageDetails]

class SessionDebugDetails(BaseModel):
    debuggerFullscreenUrl: str
    debuggerUrl: str
    pages: PageList
    wsUrl: str

class RequestDetails(BaseModel):
    timestamp: int
    params: Dict[str, Any] = {}
    rawBody: Optional[str] = None

class ResponseDetails(BaseModel):
    timestamp: int
    result: Dict[str, Any]
    rawBody: Optional[str] = None

class LogEntry(BaseModel):
    method: str
    pageId: int
    sessionId: str
    request: RequestDetails
    response: ResponseDetails
    timestamp: int
    frameId: str
    loaderId: str

class LogEntryList(BaseModel):
    items: List[LogEntry]

class RecordingEntry(BaseModel):
    data: Dict[str, Any] = {}
    sessionId: str
    timestamp: int
    type: int

class RecordingEntryList(BaseModel):
    items: List[RecordingEntry]

# Response Wrapper Models
class GetSessionResponse(BaseModel):
    data: SessionDetails

class CreateSessionResponse(BaseModel):
    data: SessionDetails

class UpdateSessionResponse(BaseModel):
    data: SessionDetails

class ListSessionsResponse(BaseModel):
    data: SessionList

class GetContextResponse(BaseModel):
    data: ContextDetails

class CreateContextResponse(BaseModel):
    data: ContextDetails

class SessionLogsResponse(BaseModel):
    data: LogEntryList

class SessionRecordingResponse(BaseModel):
    data: RecordingEntryList

class SessionDebugResponse(BaseModel):
    data: SessionDebugDetails

class SessionUploadsResponse(BaseModel):
    data: Dict[str, str]
    
# Response Models for Projects
class ProjectDetails(BaseModel):
    id: str
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None
    name: Optional[str] = None
    ownerId: Optional[str] = None
    defaultTimeout: Optional[int] = None

class ProjectList(BaseModel):
    items: List[ProjectDetails]

class ProjectUsage(BaseModel):
    browserMinutes: int
    proxyBytes: int

# Response Wrapper Models for Projects
class ListProjectsResponse(BaseModel):
    data: ProjectList

class GetProjectResponse(BaseModel):
    data: ProjectDetails

class GetProjectUsageResponse(BaseModel):
    data: ProjectUsage

# Response Models for Extensions
class ExtensionDetails(BaseModel):
    id: str
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None
    fileName: Optional[str] = None
    projectId: Optional[str] = None

# Response Wrapper Models for Extensions
class GetExtensionResponse(BaseModel):
    data: ExtensionDetails

class UploadExtensionResponse(BaseModel):
    data: ExtensionDetails

# API Response
class ApiResponse(BaseModel):
    data: Union[
        SessionDetails, 
        SessionList, 
        ContextDetails, 
        LogEntryList, 
        RecordingEntryList,
        SessionDebugDetails,
        ProjectDetails,
        ProjectList,
        ProjectUsage,
        ExtensionDetails,
        Dict[str, str]
    ]
    component: Optional[Dict[str, Any]] = None
