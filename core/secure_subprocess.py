#!/usr/bin/env python3
"""
Secure Subprocess Manager - Safe subprocess execution with input sanitization

This module addresses the security concerns from the code review by providing:
- Input sanitization for all subprocess calls
- Secure subprocess execution with timeouts
- Comprehensive logging and error handling
- Async subprocess support
- Resource monitoring and cleanup

Author: Emotional AI System
Date: August 3, 2025
"""

import asyncio
import logging
import shlex
import subprocess
import time
import re
import os
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass
from pathlib import Path
import signal
import threading

logger = logging.getLogger(__name__)

@dataclass
class SubprocessResult:
    """Result of subprocess execution"""
    returncode: int
    stdout: str
    stderr: str
    execution_time: float
    command: str
    sanitized_command: str

class SecurityError(Exception):
    """Raised when security validation fails"""
    pass

class SubprocessManager:
    """Secure subprocess execution manager"""
    
    def __init__(self):
        self.allowed_commands = {
            # System commands
            "ls", "dir", "cat", "type", "head", "tail", "wc", "grep", "find",
            # Development tools  
            "python", "pip", "git", "npm", "node",
            # File operations
            "cp", "copy", "mv", "move", "rm", "del", "mkdir", "rmdir",
            # Network tools (restricted)
            "ping", "curl", "wget"
        }
        
        self.dangerous_patterns = [
            r"[;&|`$()]",  # Shell injection characters
            r"\.\.\/",      # Directory traversal
            r"\/etc\/",     # System directories
            r"\/proc\/",    # Process filesystem
            r"rm\s+-rf",    # Dangerous deletion
            r"sudo",        # Privilege escalation
            r"su\s",        # User switching
            r"chmod\s+[0-9]*7", # Dangerous permissions
        ]
        
        self.max_execution_time = 30  # seconds
        self.max_output_size = 1024 * 1024  # 1MB
        
        # Track running processes
        self.running_processes = {}
        self._cleanup_thread = None
        self._start_cleanup_thread()
    
    def _start_cleanup_thread(self):
        """Start background thread for process cleanup"""
        if self._cleanup_thread and self._cleanup_thread.is_alive():
            return
            
        self._cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self._cleanup_thread.start()
    
    def _cleanup_loop(self):
        """Background cleanup of old processes"""
        while True:
            try:
                current_time = time.time()
                expired_processes = []
                
                for pid, (process, start_time) in self.running_processes.items():
                    if current_time - start_time > self.max_execution_time:
                        expired_processes.append(pid)
                
                for pid in expired_processes:
                    try:
                        process, _ = self.running_processes.pop(pid)
                        if process.poll() is None:  # Still running
                            process.terminate()
                            logger.warning(f"Terminated long-running process {pid}")
                    except Exception as e:
                        logger.error(f"Error cleaning up process {pid}: {e}")
                
                time.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                time.sleep(10)
    
    def sanitize_command(self, command: Union[str, List[str]]) -> List[str]:
        """Sanitize command input to prevent injection attacks"""
        if isinstance(command, str):
            # Split command string safely
            try:
                command_parts = shlex.split(command)
            except ValueError as e:
                raise SecurityError(f"Invalid command syntax: {e}")
        else:
            command_parts = command.copy()
        
        if not command_parts:
            raise SecurityError("Empty command")
        
        # Check if base command is allowed
        base_command = Path(command_parts[0]).name
        if base_command not in self.allowed_commands:
            raise SecurityError(f"Command '{base_command}' not in allowed list")
        
        # Check for dangerous patterns
        full_command = " ".join(command_parts)
        for pattern in self.dangerous_patterns:
            if re.search(pattern, full_command, re.IGNORECASE):
                raise SecurityError(f"Command contains dangerous pattern: {pattern}")
        
        # Sanitize arguments
        sanitized_parts = []
        for part in command_parts:
            # Remove null bytes and control characters
            sanitized_part = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', part)
            
            # Escape shell metacharacters
            sanitized_part = shlex.quote(sanitized_part)
            sanitized_parts.append(sanitized_part)
        
        return sanitized_parts
    
    def validate_working_directory(self, cwd: Optional[str] = None) -> Optional[str]:
        """Validate and sanitize working directory"""
        if cwd is None:
            return None
        
        # Resolve to absolute path
        cwd_path = Path(cwd).resolve()
        
        # Check if directory exists
        if not cwd_path.exists():
            raise SecurityError(f"Working directory does not exist: {cwd}")
        
        if not cwd_path.is_dir():
            raise SecurityError(f"Working directory is not a directory: {cwd}")
        
        # Check for dangerous directories
        dangerous_dirs = ["/etc", "/proc", "/sys", "/dev"]
        if os.name != 'nt':  # Unix-like systems
            for dangerous_dir in dangerous_dirs:
                if str(cwd_path).startswith(dangerous_dir):
                    raise SecurityError(f"Access to directory not allowed: {cwd}")
        
        return str(cwd_path)
    
    def execute_safe(self, 
                    command: Union[str, List[str]],
                    cwd: Optional[str] = None,
                    timeout: Optional[float] = None,
                    capture_output: bool = True,
                    input_data: Optional[str] = None) -> SubprocessResult:
        """Execute command safely with input sanitization"""
        
        start_time = time.time()
        original_command = command if isinstance(command, str) else " ".join(command)
        
        try:
            # Sanitize command
            sanitized_command = self.sanitize_command(command)
            
            # Validate working directory
            safe_cwd = self.validate_working_directory(cwd)
            
            # Set timeout
            if timeout is None:
                timeout = self.max_execution_time
            else:
                timeout = min(timeout, self.max_execution_time)
            
            # Prepare environment
            env = os.environ.copy()
            # Remove dangerous environment variables
            dangerous_env_vars = ["LD_PRELOAD", "LD_LIBRARY_PATH", "DYLD_INSERT_LIBRARIES"]
            for var in dangerous_env_vars:
                env.pop(var, None)
            
            logger.info(f"Executing safe subprocess: {' '.join(sanitized_command)}")
            
            # Execute subprocess
            if capture_output:
                process = subprocess.Popen(
                    sanitized_command,
                    cwd=safe_cwd,
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.PIPE if input_data else None,
                    text=True,
                    shell=False  # Never use shell=True
                )
            else:
                process = subprocess.Popen(
                    sanitized_command,
                    cwd=safe_cwd,
                    env=env,
                    shell=False
                )
            
            # Track running process
            self.running_processes[process.pid] = (process, start_time)
            
            try:
                # Wait for completion with timeout
                stdout, stderr = process.communicate(input=input_data, timeout=timeout)
                returncode = process.returncode or 0
                
                # Convert to string if needed and limit output size
                stdout_str = str(stdout) if stdout else ""
                stderr_str = str(stderr) if stderr else ""
                
                if len(stdout_str) > self.max_output_size:
                    stdout_str = stdout_str[:self.max_output_size] + "\n[OUTPUT TRUNCATED]"
                
                if len(stderr_str) > self.max_output_size:
                    stderr_str = stderr_str[:self.max_output_size] + "\n[OUTPUT TRUNCATED]"
                
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                returncode = -1
                stdout_str = str(stdout) if stdout else ""
                stderr_str = (str(stderr) if stderr else "") + "\n[PROCESS KILLED: TIMEOUT]"
                
            finally:
                # Remove from tracking
                self.running_processes.pop(process.pid, None)
            
            execution_time = time.time() - start_time
            
            result = SubprocessResult(
                returncode=returncode,
                stdout=stdout_str,
                stderr=stderr_str,
                execution_time=execution_time,
                command=original_command,
                sanitized_command=" ".join(sanitized_command)
            )
            
            logger.info(f"Subprocess completed in {execution_time:.2f}s with return code {returncode}")
            return result
            
        except SecurityError:
            raise
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Subprocess execution failed: {e}")
            
            return SubprocessResult(
                returncode=-1,
                stdout="",
                stderr=f"Execution failed: {str(e)}",
                execution_time=execution_time,
                command=original_command,
                sanitized_command=""
            )
    
    async def execute_async(self, 
                           command: Union[str, List[str]],
                           cwd: Optional[str] = None,
                           timeout: Optional[float] = None,
                           input_data: Optional[str] = None) -> SubprocessResult:
        """Execute command asynchronously with safety checks"""
        
        start_time = time.time()
        original_command = command if isinstance(command, str) else " ".join(command)
        
        try:
            # Sanitize command
            sanitized_command = self.sanitize_command(command)
            
            # Validate working directory
            safe_cwd = self.validate_working_directory(cwd)
            
            # Set timeout
            if timeout is None:
                timeout = self.max_execution_time
            else:
                timeout = min(timeout, self.max_execution_time)
            
            logger.info(f"Executing async subprocess: {' '.join(sanitized_command)}")
            
            # Create async subprocess
            process = await asyncio.create_subprocess_exec(
                *sanitized_command,
                cwd=safe_cwd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                stdin=asyncio.subprocess.PIPE if input_data else None
            )
            
            try:
                # Communicate with timeout
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(input=input_data.encode() if input_data else None),
                    timeout=timeout
                )
                
                returncode = process.returncode
                
                # Decode output
                stdout_str = stdout.decode('utf-8', errors='replace') if stdout else ""
                stderr_str = stderr.decode('utf-8', errors='replace') if stderr else ""
                
                # Limit output size
                if len(stdout_str) > self.max_output_size:
                    stdout_str = stdout_str[:self.max_output_size] + "\n[OUTPUT TRUNCATED]"
                
                if len(stderr_str) > self.max_output_size:
                    stderr_str = stderr_str[:self.max_output_size] + "\n[OUTPUT TRUNCATED]"
                
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                returncode = -1
                stdout_str = ""
                stderr_str = "[PROCESS KILLED: TIMEOUT]"
            
            execution_time = time.time() - start_time
            
            result = SubprocessResult(
                returncode=returncode or 0,
                stdout=stdout_str,
                stderr=stderr_str,
                execution_time=execution_time,
                command=original_command,
                sanitized_command=" ".join(sanitized_command)
            )
            
            logger.info(f"Async subprocess completed in {execution_time:.2f}s with return code {returncode}")
            return result
            
        except SecurityError:
            raise
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Async subprocess execution failed: {e}")
            
            return SubprocessResult(
                returncode=-1,
                stdout="",
                stderr=f"Execution failed: {str(e)}",
                execution_time=execution_time,
                command=original_command,
                sanitized_command=""
            )
    
    def add_allowed_command(self, command: str):
        """Add a command to the allowed list"""
        self.allowed_commands.add(command)
        logger.info(f"Added allowed command: {command}")
    
    def remove_allowed_command(self, command: str):
        """Remove a command from the allowed list"""
        if command in self.allowed_commands:
            self.allowed_commands.remove(command)
            logger.info(f"Removed allowed command: {command}")
    
    def get_running_processes(self) -> Dict[int, Tuple[Any, float]]:
        """Get currently running processes"""
        return self.running_processes.copy()
    
    def kill_all_processes(self):
        """Kill all tracked running processes"""
        for pid, (process, _) in list(self.running_processes.items()):
            try:
                if process.poll() is None:  # Still running
                    process.kill()
                    logger.info(f"Killed process {pid}")
            except Exception as e:
                logger.error(f"Error killing process {pid}: {e}")
        
        self.running_processes.clear()

# Global subprocess manager instance
subprocess_manager = SubprocessManager()

# Convenience functions for safe subprocess execution
def safe_execute(command: Union[str, List[str]], **kwargs) -> SubprocessResult:
    """Execute command safely with input sanitization"""
    return subprocess_manager.execute_safe(command, **kwargs)

async def safe_execute_async(command: Union[str, List[str]], **kwargs) -> SubprocessResult:
    """Execute command asynchronously with safety checks"""
    return await subprocess_manager.execute_async(command, **kwargs)

def add_allowed_command(command: str):
    """Add a command to the allowed list"""
    subprocess_manager.add_allowed_command(command)

def kill_all_processes():
    """Kill all tracked running processes"""
    subprocess_manager.kill_all_processes()
