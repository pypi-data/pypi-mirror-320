from contextlib import contextmanager
from functools import wraps
import os
from typing import Callable, Optional
import builtins
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class IORedirectManager:
    """
    Manages I/O redirection for Pipeline UI nodes and workflows.
    Redirects user code I/O operations to /tmp while preserving original paths for system operations.
    """
    def __init__(self, enable_io_redirect: bool = True, user_code_root: Optional[str] = None):
        self.base_path = "/tmp"
        self.user_code_root = user_code_root or os.getcwd()
        os.makedirs(self.base_path, exist_ok=True)
        self._active = enable_io_redirect
        self._original_open = builtins.open

    def should_redirect_path(self, path: str) -> bool:
        """
        Smart path detection based on path characteristics:
        - Paths within the user's project directory are redirected
        - Absolute paths outside the project directory maintain their location
        - Hidden directories (starting with .) maintain their location
        """
        abs_path = os.path.abspath(path)
        path_obj = Path(abs_path)
        
        # Never redirect hidden directories (like .cache)
        if any(part.startswith('.') for part in path_obj.parts):
            return False
            
        # Check if path is within user code directory
        try:
            path_obj.relative_to(self.user_code_root)
            return True
        except ValueError:
            return False
        
    def resolve_path(self, path: str) -> str:
        """
        Resolves a path based on whether it should be redirected:
        - Paths meeting redirect criteria go to /tmp
        - Other paths maintain their original location
        """
        if not self._active:
            return path
            
        if not self.should_redirect_path(path):
            return path
            
        filename = os.path.basename(path)
        resolved_path = os.path.join(self.base_path, filename)
        
        print(
            f"Due to Beam cloud internal requirements, the path '{path}' has been automatically "
            f"rewritten to '{resolved_path}' as /tmp is the only writable directory in a Beam container"
        )
        
        return resolved_path
        
    @contextmanager
    def managed_context(self):
        """Context manager for I/O redirection"""
        original_open = builtins.open
        
        def redirected_open(file, *args, **kwargs):
            resolved_path = self.resolve_path(file)
            if resolved_path.startswith('/tmp'):
                os.makedirs(self.base_path, exist_ok=True)
            return original_open(resolved_path, *args, **kwargs)
            
        builtins.open = redirected_open
        try:
            yield
        finally:
            builtins.open = original_open

def io_wrapper(func: Callable, io_manager: IORedirectManager) -> Callable:
    """Wrapper to add I/O redirection to a function"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        with io_manager.managed_context():
            return func(*args, **kwargs)
    return wrapper