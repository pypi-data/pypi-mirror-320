import ast
import inspect
import textwrap
from pathlib import Path
from typing import Callable, Dict, List, Optional, Set

from pydantic import BaseModel, Field


class FunctionInfo(BaseModel):
    """Pydantic model for storing function information"""
    source_code: str
    name: str
    called_functions: List[str] = Field(default_factory=list)

    docstring: Optional[str] = None
    module: str
    line_number: int
    is_async: bool = False
    decorators: List[str] = Field(default_factory=list)
    imports: List[str] = Field(default_factory=list)


class ImportExtractor(ast.NodeVisitor):
    """AST visitor to find all imports in a module"""
    def __init__(self):
        self.imports = []
        
    def visit_Import(self, node):
        for name in node.names:
            self.imports.append(f"import {name.name}")
            
    def visit_ImportFrom(self, node):
        module = node.module or ''
        names = [n.name for n in node.names]
        self.imports.append(f"from {module} import {', '.join(names)}")


class FunctionExtractor(ast.NodeVisitor):
    """AST visitor to find all function calls within a function"""
    def __init__(self):
        self.function_calls = set()
        
    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            self.function_calls.add(node.func.id)
        self.generic_visit(node)


def get_all_function_calls(source_code: str) -> Set[str]:
    """Extract all function names that are called within the given source code."""
    tree = ast.parse(source_code)
    extractor = FunctionExtractor()
    extractor.visit(tree)
    return extractor.function_calls


def get_imports(source_code: str) -> List[str]:
    """Extract all imports from the source code."""
    tree = ast.parse(source_code)
    extractor = ImportExtractor()
    extractor.visit(tree)
    return extractor.imports


def is_user_defined_function(func: Callable) -> bool:
    """Check if a function is user-defined (not from a library)."""
    try:
        module = inspect.getmodule(func)
        if module is None:
            return False
            
        file_path = Path(inspect.getfile(func))
        return not any(part.startswith(('site-packages', 'dist-packages', 'lib'))
                      for part in file_path.parts)
    except (TypeError, OSError):
        return False


def create_function_info(func: Callable) -> Optional[FunctionInfo]:
    """Create a FunctionInfo instance for a given function."""
    # try:
    # Get the module source code and imports
    module = inspect.getmodule(func)
    if module is not None:
        module_source = inspect.getsource(module)
        imports = get_imports(module_source)
    else:
        assert False, "module is None"
        imports = []
    
    # Get the function source code
    source = inspect.getsource(func)
    source = textwrap.dedent(source)
    
    # Parse the source into an AST
    tree = ast.parse(source)
    function_def = tree.body[0]  # Assume the function is the first item
    
    # Get called functions
    called_funcs = get_all_function_calls(source)
    
    # Get decorators
    decorators = []
    if isinstance(function_def, ast.FunctionDef):
        for decorator in function_def.decorator_list:
            if isinstance(decorator, ast.Name):
                decorators.append(decorator.id)
            elif isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Name):
                    decorators.append(decorator.func.id)
    else:
        decorators = []
    
    # Combine imports and source
    # full_source = "\n".join(imports + ["", source])
    
    return FunctionInfo(
        source_code=source,
        name=func.__name__,
        docstring=inspect.getdoc(func),
        module=func.__module__ or "",
        line_number=inspect.getsourcelines(func)[1],
        is_async=isinstance(function_def, ast.AsyncFunctionDef),
        decorators=decorators,
        imports=imports,
        called_functions=list(called_funcs)
    )
    # except (TypeError, OSError) as e:
        # print("error extracting function info", e)
        # return None


def extract_function_code_recursive(func: Callable, extracted_funcs: Optional[Dict[str, FunctionInfo]] = None, recursive = True) -> Dict[str, FunctionInfo]:
    """
    Recursively extract information about a function and all user-defined functions it calls.
    
    Args:
        func: The root function to start extraction from
        extracted_funcs: Dictionary of already extracted functions to prevent infinite recursion
        
    Returns:
        Dict[str, FunctionInfo]: Dictionary mapping function names to their FunctionInfo objects
    """
    # print("extracting function code recursively, func:", func.__name__)
    # get code of func
    # source = inspect.getsource(func)
    # print("source", source)
    # raise Exception("test")

    if func.__name__ == "node" or func.__name__ == "workflow":
        return {}

    if extracted_funcs is None:
        extracted_funcs = {}
        
    # If we've already extracted this function, skip it
    if func.__name__ in extracted_funcs:
        # print("already extracted, skipping")
        return extracted_funcs
        
    # Create FunctionInfo for current function
    func_info = create_function_info(func)
    if func_info is None:
        # print("func_info is None, skipping")
        return extracted_funcs
        
    extracted_funcs[func.__name__] = func_info
    
    # Get the module where the function is defined
    module = inspect.getmodule(func)
    if module is None:
        # print("module is None, skipping")
        return extracted_funcs
        
    if recursive:
        # For each called function, recursively extract its info if it's user-defined
        for called_func_name in func_info.called_functions:
            if hasattr(module, called_func_name):
                called_func = getattr(module, called_func_name)
                if (inspect.isfunction(called_func) and 
                    is_user_defined_function(called_func) and 
                    called_func_name not in extracted_funcs):
                    extract_function_code_recursive(called_func, extracted_funcs)

    assert func.__name__ in extracted_funcs, f"Function {func.__name__} not extracted"
    # print("extracted_funcs", extracted_funcs)
    return extracted_funcs