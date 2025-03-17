from typing import Optional, Dict, List, Any
from e2b_code_interpreter import Sandbox
import os
import base64

class E2BClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        
    
    def create_sandbox(self, timeout: int = 300, env: Optional[Dict[str, str]] = None, metadata: Optional[Dict[str, str]] = None) -> Dict:
        """Create a new E2B sandbox environment"""
        sandbox = Sandbox(api_key=self.api_key, timeout=timeout, envs=env, metadata=metadata)
        return sandbox
    
    def list_sandboxes(self) -> List[Dict]:
        try:
            # Get list of running sandboxes
            running_sandboxes = Sandbox.list(api_key=self.api_key)
            
            # Convert to list of dictionaries with relevant information
            result = []
            for sandbox in running_sandboxes:
                sandbox_info = {
                    "id": sandbox.sandbox_id,
                    "metadata": sandbox.metadata if hasattr(sandbox, 'metadata') else None,
                    "started_at": sandbox.started_at if hasattr(sandbox, 'started_at') else None,
                    "template_id": sandbox.template_id if hasattr(sandbox, 'template_id') else None
                }
                result.append(sandbox_info)
                
            return result
        except Exception as e:
            print(f"Error listing sandboxes: {str(e)}")
            return []

    def run_command(self, sandbox_id: str, command: str, background: bool = False) -> Dict:
        try:
            # Reconnect to the sandbox
            sandbox = Sandbox(api_key=self.api_key, sandbox_id=sandbox_id)
            
            # Run the command
            proc = sandbox.commands.run(command, background=background)

            if background:
                return {
                    "stdout": "",
                    "stderr": "",
                    "exit_code": 0,
                    "error": None
                }
            # Process the results
            return {
                "stdout": proc.stdout if hasattr(proc, 'stdout') else "",
                "stderr": proc.stderr if hasattr(proc, 'stderr') else "",
                "exit_code": proc.exit_code,
                "error": None
            }
        except Exception as e:
            return {
                "stdout": "",
                "stderr": "",
                "exit_code": 1,
                "error": str(e) + " Hint: check if sandbox is running"
            }

    def pause_sandbox(self, sandbox_id: str) -> Dict:
        """
        Pause a sandbox to save its state for later resumption
        
        Args:
            sandbox_id: ID of the sandbox to pause
            
        Returns:
            Dict containing the paused sandbox ID and status
        """
        try:
            with Sandbox.reconnect(sandbox_id, self.api_key) as sandbox:
                paused_id = sandbox.pause()
                return {
                    "id": paused_id,
                    "status": "paused"
                }
        except Exception as e:
            return {
                "id": sandbox_id,
                "status": "error",
                "error": str(e)
            }
    
    def resume_sandbox(self, sandbox_id: str, timeout: int = 300) -> Dict:
        """
        Resume a previously paused sandbox
        
        Args:
            sandbox_id: ID of the paused sandbox to resume
            timeout: New timeout for the resumed sandbox in seconds
            
        Returns:
            Dict containing the resumed sandbox details
        """
        try:
            print("trying to resume sandbox")
            sandbox = Sandbox.resume(sandbox_id, api_key=self.api_key, timeout=300)
            print("sandbox resumed", sandbox)
            return {
                "id": sandbox.id,
                "timeout": timeout,
                "status": "active"
            }
        except Exception as e:
            print("error resuming sandbox", e)
            return {
                "id": sandbox_id,
                "status": "error",
                "error": str(e)
            }

    def run_code(self, code: str, sandbox_id: Optional[str]=None, language: str = "python", commands: Optional[List[str]] = None, env: Optional[Dict[str, str]] = None) -> Dict:
        sandbox = Sandbox(api_key=self.api_key, sandbox_id=sandbox_id)
        
        # Run any commands if specified
        if commands:
            for cmd in commands:
                sandbox.commands.run(cmd)
        
        # Execute code in the specified language
        execution = sandbox.run_code(code, language, envs=env)
        
        # Process results including any generated files
        files_dict = {}
        if hasattr(execution, 'results') and execution.results:
            for i, result in enumerate(execution.results):
                # Check for various file formats and add to files_dict if present
                for fmt in ['png', 'jpg', 'pdf', 'svg']:
                    if hasattr(result, fmt) and getattr(result, fmt):
                        files_dict[f"result_{i}.{fmt}"] = getattr(result, fmt)
        
        return {
            "logs": {
                "stdout": execution.logs.stdout if hasattr(execution, 'logs') and hasattr(execution.logs, 'stdout') else [],
                "stderr": execution.logs.stderr if hasattr(execution, 'logs') and hasattr(execution.logs, 'stderr') else []
            },
            "error": execution.error if hasattr(execution, 'error') else None,
            "exit_code": 1 if hasattr(execution, 'error') and execution.error else 0,
            "files": files_dict
        }

    def get_host(self, sandbox_id: str, port: int) -> str:
        sandbox = Sandbox(api_key=self.api_key, sandbox_id=sandbox_id)
        
        host = sandbox.get_host(port) 
        return "https://" + host

    def kill_sandbox(self, sandbox_id: str) -> Dict:
        sandbox = Sandbox(api_key=self.api_key, sandbox_id=sandbox_id)
        sandbox.kill()
        return {"message": "Sandbox terminated"}

    def upload_file(self, sandbox_id: str, path: str, content: str, encoding: str = "utf-8") -> Dict:
        """
        Upload a file to the specified path in the sandbox
        
        Args:
            sandbox_id: ID of the sandbox
            path: Destination path in the sandbox
            content: File content as string or base64 encoded string
            encoding: 'utf-8' or 'base64'
            
        Returns:
            Dict with the result of the operation
        """
        try:
            # Reconnect to the sandbox
            sandbox = Sandbox(api_key=self.api_key, sandbox_id=sandbox_id)
            
            # Convert content to bytes based on encoding
            file_bytes = None
            if encoding.lower() == "base64":
                file_bytes = base64.b64decode(content)
            else:
                file_bytes = content.encode("utf-8")
            
            # Upload the file to the sandbox
            sandbox.files.write(path, file_bytes)
            
            return {
                "path": path,
                "success": True,
                "message": "File uploaded successfully"
            }
        except Exception as e:
            return {
                "path": path,
                "success": False,
                "message": f"Error uploading file: {str(e)}"
            }
    
    def download_file(self, sandbox_id: str, path: str, encoding: str = "utf-8") -> Dict:
       
        try:
            # Reconnect to the sandbox
            sandbox = Sandbox(api_key=self.api_key, sandbox_id=sandbox_id)
            
            # Download the file content as bytes
            file_content = sandbox.files.read(path)
            
            # If the user wants base64, encode the (already string) content to bytes, 
            # then base64-encode it, then convert back to a string.
            if encoding.lower() == "base64":
                encoded_bytes = base64.b64encode(file_content.encode("utf-8"))
                content = encoded_bytes.decode("utf-8")
            else:
                # Default or "utf-8": simply return the string content as-is
                content = file_content

            return {
                "path": path,
                "content": content,
                "encoding": encoding,
                "success": True
            }
            
        except Exception as e:
            return {
                "path": path,
                "content": "",
                "encoding": encoding,
                "success": False,
                "message": f"Error downloading file: {str(e)}"
            }
