from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List

class SandboxCreateRequest(BaseModel):
    timeout: int = Field(300, description="Sandbox lifetime in seconds")
    initial_code: Optional[str] = Field(None, description="Code to run on startup")
    env: Optional[Dict[str, str]] = Field(None, description="Environment variables to set")
    metadata: Optional[Dict[str, str]] = Field(None, description="Metadata for the sandbox")

class SandboxListRequest(BaseModel):
    pass

class SandboxRunCommandRequest(BaseModel):
    sandbox_id: str = Field(..., description="ID of active sandbox")
    command: str = Field(..., description="Command to run")

class SandboxPauseRequest(BaseModel):
    sandbox_id: str = Field(..., description="ID of active sandbox to pause")

class SandboxResumeRequest(BaseModel):
    sandbox_id: str = Field(..., description="ID of paused sandbox to resume")
    timeout: int = Field(300, description="New timeout for resumed sandbox in seconds")

class SandboxTerminateRequest(BaseModel):
    sandbox_id: str = Field(..., description="ID of sandbox to terminate")

class CodeExecutionRequest(BaseModel):
    code: str = Field(..., description="Code to execute")
    sandbox_id: Optional[str] = Field(None, description="ID of active sandbox")
    language: Optional[str] = Field("python", description="Programming language to use: python, js, r, java, bash")
    commands: Optional[List[str]] = Field(None, description="Shell commands to run before code execution")
    env: Optional[Dict[str, str]] = Field(None, description="Environment variables to set")

class FileListRequest(BaseModel):
    sandbox_id: str = Field(..., description="ID of active sandbox")
    path: str = Field("/", description="Directory path to list")

class SandboxSession(BaseModel):
    id: str
    timeout: int
    metadata: Optional[Dict[str, str]] = None
    started_at: Optional[str] = None
    template_id: Optional[str] = None

class SandboxInfo(BaseModel):
    id: str
    metadata: Optional[Dict[str, str]] = None
    started_at: Optional[str] = None
    template_id: Optional[str] = None

class CommandExecutionResult(BaseModel):
    stdout: str
    stderr: str
    exit_code: int
    error: Optional[str] = None

class CodeExecutionResult(BaseModel):
    stdout: str
    stderr: str
    error: Optional[str]
    exit_code: int
    files: Optional[Dict[str, str]] = Field(None, description="Base64 encoded files generated during execution")

class FileListing(BaseModel):
    name: str
    is_dir: bool
    size: Optional[int]

class E2BBaseResponse(BaseModel):
    data: Dict[str, Any]
    component: Optional[Dict[str, Any]] = None

# Response schemas that properly extend E2BBaseResponse
class SandboxResponse(E2BBaseResponse):
    data: SandboxSession
    message: Optional[str] = None

class SandboxListResponse(E2BBaseResponse):
    data: List[SandboxInfo]
    message: Optional[str] = None

class CommandExecutionResponse(E2BBaseResponse):
    data: CommandExecutionResult
    message: Optional[str] = None

class CodeExecutionResponse(E2BBaseResponse):
    data: CodeExecutionResult
    message: Optional[str] = None

class FileListResponse(E2BBaseResponse):
    data: List[FileListing]
    message: Optional[str] = None

class GetHostResponse(E2BBaseResponse):
    data: str
    message: Optional[str] = None

class GetHostRequest(BaseModel):
    sandbox_id: str = Field(..., description="ID of active sandbox")
    port: int = Field(..., description="Port to get host for")

class GetHostResponse(E2BBaseResponse):
    data: str
    message: Optional[str] = None

class GetHostRequest(BaseModel):
    sandbox_id: str = Field(..., description="ID of active sandbox")
    port: int = Field(..., description="Port to get host for")