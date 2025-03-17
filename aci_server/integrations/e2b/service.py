from typing import Dict, List
from .client import E2BClient
from .schema import (
    SandboxCreateRequest,
    SandboxResponse,
    SandboxListRequest,
    SandboxListResponse,
    SandboxPauseRequest,
    SandboxResumeRequest,
    SandboxRunCommandRequest,
    CommandExecutionResponse,
    CommandExecutionResult,
    CodeExecutionRequest,
    CodeExecutionResponse,
    FileListRequest,
    FileListResponse,
    CodeExecutionResult,
    SandboxInfo,
    GetHostRequest,
    GetHostResponse
)

class E2BService:
    def __init__(self, client: E2BClient):
        self.client = client

    def create_sandbox(self, request: SandboxCreateRequest) -> SandboxResponse:
        sandbox = self.client.create_sandbox(
            timeout=request.timeout, 
            env=request.env,
            metadata=request.metadata
        )
        data = {
            "id": sandbox._sandbox_id,
            "timeout": request.timeout,
            "metadata": request.metadata
        }
        return SandboxResponse(
            data=data,
            component=None
        )
    
    def _serialize_sandbox(self, sandbox: Dict) -> SandboxInfo:
        return SandboxInfo(
            id=sandbox["id"],
            metadata=sandbox["metadata"],
            started_at=sandbox["started_at"].isoformat(),
            template_id=sandbox["template_id"]
        )

    def list_sandboxes(self, request: SandboxListRequest) -> SandboxListResponse:
        """List all running sandboxes with optional filtering"""
        sandboxes = self.client.list_sandboxes()
        
        # Convert to SandboxInfo objects
        sandbox_info_list = []
        for sandbox in sandboxes:
            sandbox_info = self._serialize_sandbox(sandbox)
            sandbox_info_list.append(sandbox_info)
        
        return SandboxListResponse(
            data=sandbox_info_list,
            component=None
        )
        
    def run_command(self, request: SandboxRunCommandRequest) -> CommandExecutionResponse:
        """Run a shell command in the sandbox"""
        result = self.client.run_command(
            sandbox_id=request.sandbox_id,
            command=request.command,
            background=request.background
        )
        
        # Create CommandExecutionResult
        execution_result = CommandExecutionResult(
            stdout=result["stdout"],
            stderr=result["stderr"],
            exit_code=result["exit_code"],
            error=result["error"]
        )
        
        return CommandExecutionResponse(
            data=execution_result,
            component=None
        )
        
    def pause_sandbox(self, request: SandboxPauseRequest) -> SandboxResponse:
        """Pause a sandbox to save its state for later resumption"""
        result = self.client.pause_sandbox(request.sandbox_id)
        
        # Create response data
        data = {
            "id": result["id"],
            "timeout": 0,  # Paused sandboxes don't have an active timeout
            "status": result["status"]
        }
        
        return SandboxResponse(
            data=data,
            component=None
        )
    
    def resume_sandbox(self, request: SandboxResumeRequest) -> SandboxResponse:
        """Resume a previously paused sandbox"""
        result = self.client.resume_sandbox(request.sandbox_id, request.timeout)
        
        # Create response data
        data = {
            "id": result["id"],
            "timeout": result["timeout"],
            "status": result["status"]
        }
        
        # Add error message if present
        message = None
        if "error" in result:
            message = f"Error resuming sandbox: {result['error']}"
        
        return SandboxResponse(
            data=data,
            component={"name": "E2BSandboxView"},
            message=message
        )

    def run_code(self, request: CodeExecutionRequest) -> CodeExecutionResponse:
        # Execute code with specified language and optional commands
        result = self.client.run_code(
            code=request.code, 
            sandbox_id=request.sandbox_id,
            language=request.language,
            commands=request.commands,
            env=request.env
        )
        
        # Extract logs from the execution result
        stdout = '\n'.join(result["logs"]["stdout"]) if result["logs"]["stdout"] else ''
        stderr = '\n'.join(result["logs"]["stderr"]) if result["logs"]["stderr"] else ''

        # Extract error information if present
        error = result["error"]
        
        # Create CodeExecutionResult
        execution_result = CodeExecutionResult(
            stdout=stdout,
            stderr=stderr,
            error=error,
            exit_code=result["exit_code"],
            files=result.get("files", None)
        )

        # Determine appropriate component based on whether files were generated
        component = None
        if result.get("files") and len(result["files"]) > 0:
            component = None
        else:
            component = None
        
        return CodeExecutionResponse(
            data=execution_result,
            component=component
        )

    def list_files(self, request: FileListRequest) -> FileListResponse:
        listing = self.client.list_files(request.sandbox_id, request.path)
        return FileListResponse(
            data=listing,
            component=None
        )

    def kill_sandbox(self, sandbox_id: str) -> Dict:
        return self.client.kill_sandbox(sandbox_id)
    
    def get_host(self, request: GetHostRequest) -> GetHostResponse:
        host = self.client.get_host(request.sandbox_id, request.port)
        return GetHostResponse(
            data=host,
            component=None
        )