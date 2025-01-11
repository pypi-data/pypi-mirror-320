import re
from typing import List, Dict, Set
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class Import:
    module: str
    items: Set[str]
    alias: str = None
    is_from: bool = False

class ImportMerger:
    def __init__(self):
        self.imports: Dict[str, Import] = {}
    
    def parse_import(self, line: str) -> Import:
        """Parse a single import statement"""
        line = line.strip()
        
        # Handle 'from' imports
        if line.startswith('from'):
            match = re.match(r'from\s+([\w.]+)\s+import\s+(.+)', line)
            if match:
                module, items = match.groups()
                items = {item.strip().split(' as ')[0] for item in items.split(',')}
                return Import(module=module, items=items, is_from=True)
        
        # Handle regular imports
        elif line.startswith('import'):
            items = line.replace('import', '').strip()
            imports = []
            for item in items.split(','):
                item = item.strip()
                if ' as ' in item:
                    module, alias = item.split(' as ')
                    return Import(module=module, items=set(), alias=alias)
                else:
                    return Import(module=item, items=set())
        
        return None

    def add_import(self, import_stmt: str):
        """Add an import statement to be merged"""
        parsed = self.parse_import(import_stmt)
        if not parsed:
            return
        
        key = parsed.module
        if key in self.imports:
            # Merge 'from' imports
            if parsed.is_from and self.imports[key].is_from:
                self.imports[key].items.update(parsed.items)
            # Handle conflicting import types
            elif parsed.is_from != self.imports[key].is_from:
                # Keep both with different keys
                key = f"{key}_{'from' if parsed.is_from else 'import'}"
                self.imports[key] = parsed
        else:
            self.imports[key] = parsed

    def optimize_imports(self):
        """Optimize imports by merging similar ones"""
        # Group imports by their base modules
        base_modules = defaultdict(list)
        for key, import_obj in list(self.imports.items()):
            base = key.split('.')[0]
            base_modules[base].append((key, import_obj))
        
        # Merge imports from same base module when possible
        for base, imports in base_modules.items():
            if len(imports) > 1:
                from_imports = [(k, i) for k, i in imports if i.is_from]
                regular_imports = [(k, i) for k, i in imports if not i.is_from]
                
                # Merge 'from' imports if they're from same module
                if len(from_imports) > 1:
                    same_module_imports = defaultdict(set)
                    for key, import_obj in from_imports:
                        same_module_imports[import_obj.module].update(import_obj.items)
                        del self.imports[key]
                    
                    for module, items in same_module_imports.items():
                        self.imports[module] = Import(module=module, items=items, is_from=True)
                
                # Consider merging regular imports into a single import
                if len(regular_imports) > 1:
                    modules = [i.module for _, i in regular_imports]
                    if all(m.startswith(f"{base}.") for m in modules):
                        for key, _ in regular_imports:
                            del self.imports[key]
                        self.imports[base] = Import(module=base, items=set())

    def format_import(self, import_obj: Import) -> str:
        """Format an import object into a string"""
        if import_obj.is_from:
            items = sorted(import_obj.items)
            if len(items) > 3:  # Use multi-line format for many items
                items_str = '(\n    ' + ',\n    '.join(items) + '\n)'
            else:
                items_str = ', '.join(items)
            return f"from {import_obj.module} import {items_str}"
        else:
            if import_obj.alias:
                return f"import {import_obj.module} as {import_obj.alias}"
            return f"import {import_obj.module}"

    def merge(self, import_statements: List[str]) -> str:
        """Merge multiple import statements into optimized imports"""
        # Clear previous imports
        self.imports.clear()
        
        # Add all imports
        for stmt in import_statements:
            self.add_import(stmt)
        
        # Optimize imports
        self.optimize_imports()
        
        # Group imports by type
        std_lib_imports = []
        third_party_imports = []
        local_imports = []
        
        for key in sorted(self.imports.keys()):
            import_obj = self.imports[key]
            import_str = self.format_import(import_obj)
            
            # Simple classification (can be improved)
            if '.' not in key:
                std_lib_imports.append(import_str)
            elif key.startswith('.'):
                local_imports.append(import_str)
            else:
                third_party_imports.append(import_str)
        
        # Combine all imports with proper spacing
        result = []
        if std_lib_imports:
            result.extend(std_lib_imports)
        if third_party_imports:
            if result:
                result.append('')
            result.extend(third_party_imports)
        if local_imports:
            if result:
                result.append('')
            result.extend(local_imports)
        
        return '\n'.join(result)

# Example usage
if __name__ == "__main__":
    merger = ImportMerger()
    imports = [
        "from typing import List, Dict",
        "from typing import Set, Optional",
        "import os",
        "import sys",
        "from os.path import join",
        "from os.path import dirname",
        "import pandas as pd",
        "import numpy as np",
        "from .utils import helper",
        "from . import constants"
    ]
    
    result = merger.merge(imports)
    print(result)