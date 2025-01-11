import os
import sys
import importlib.util
from typing import Dict, List, Set, Optional
import inspect

class ModuleAutoloader:
    def __init__(self):
        self.loaded_modules: Set[str] = set()
        self.modules: Dict[str, Any] = {}  # Store module references
        self.module_sources: Dict[str, str] = {}  # Store module source codes

    def _is_python_file(self, path: str) -> bool:
        return path.endswith('.py') and not os.path.basename(path).startswith('_')

    def _has_decorators(self, file_path: str) -> bool:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                return '@node' in content or '@workflow' in content
        except:
            return False
    
    def _import_module(self, file_path: str) -> Optional[bool]:
        # try:
        # Get absolute path
        abs_path = os.path.abspath(file_path)
        
        # Convert file path to module name
        rel_path = os.path.relpath(abs_path, os.path.dirname(sys.argv[0]))
        module_name = os.path.splitext(rel_path)[0].replace(os.path.sep, '.')
        
        if module_name in self.loaded_modules:
            return None
            
        # Check for decorators
        if not self._has_decorators(abs_path):
            return None
        
        # Read and store the source code before importing
        with open(abs_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
            self.module_sources[module_name] = source_code
        
        # Import the module
        spec = importlib.util.spec_from_file_location(module_name, abs_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            
            # Store source code in module for inspect to find
            module.__source__ = source_code
            
            # Add to sys.modules before execution
            sys.modules[module_name] = module
            
            # Execute the module
            spec.loader.exec_module(module)
            
            # Store reference to prevent garbage collection
            self.modules[module_name] = module
            self.loaded_modules.add(module_name)
            
            # Patch inspect.getsource to return our stored source
            original_getsource = inspect.getsource
            def patched_getsource(obj):
                if hasattr(obj, '__module__') and obj.__module__ in self.module_sources:
                    return self.module_sources[obj.__module__]
                return original_getsource(obj)
            inspect.getsource = patched_getsource
            
            print(f"Imported module '{module_name}' from {file_path}")
            return True
                
        # except Exception as e:
        #     print(f"Error importing {file_path}: {str(e)}")
        #     print("Please make sure the file is a valid python file otherwise it will not be loaded and you will not see it in the UI")
        #     return False
            
        return None

    def scan_directory_for_pui(self, directory: str, subdirs: List[str] = None) -> None:
        if not os.path.exists(directory):
            return
            
        directory = os.path.abspath(directory)
        if directory not in sys.path:
            sys.path.insert(0, directory)
            
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if not d.startswith('_')]
            
            if subdirs:
                current_dir = os.path.basename(root)
                parent_dir = os.path.basename(os.path.dirname(root))
                if current_dir not in subdirs and parent_dir not in subdirs:
                    continue
            
            for file in files:
                if self._is_python_file(file):
                    file_path = os.path.join(root, file)
                    self._import_module(file_path)