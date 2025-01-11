from textwrap import dedent
from typing import Callable, Dict, Any, Union, get_type_hints
import inspect
from dataclasses import dataclass
from enum import Enum, auto
import ast
from typing import Annotated
from devtools import debug
from typing import Callable, Dict, List, Union

from pipeline_ui.modules.testing.testing_var import TESTING


class Node(Enum):
    CLIP_TEXT_ENCODE = auto()
    LOAD_CHECKPOINT = auto()
    VAE_DECODE = auto()
    SAVE_IMAGE = auto()

@dataclass
class TextParameter:
    description: str

# Map known function names to Node types
func_to_node = {
    'load_checkpoint': Node.LOAD_CHECKPOINT,
    'clip_text_encode': Node.CLIP_TEXT_ENCODE,
    'vae_decode': Node.VAE_DECODE,
    'save_image': Node.SAVE_IMAGE
}

def extract_function_calls(func: Callable) -> Dict[str, List[Dict]]:
    """
    Extract function calls and their arguments from the function body.
    
    Returns:
        Dict[str, list]: A dictionary mapping function names to lists of argument assignments
    """
    source = inspect.getsource(func)


    if TESTING:
        source = dedent(source)

    tree = ast.parse(source)
    
    class FunctionCallVisitor(ast.NodeVisitor):
        def __init__(self):
            self.calls = {}
            
        def visit_Call(self, node):
            func_name = self._get_func_name(node.func)
            if func_name:
                if func_name not in self.calls:
                    self.calls[func_name] = []
                
                call_info = {
                    'pos_args': [],
                    'kwargs': [],
                    'raw_call': ast.unparse(node)
                }
                
                # Collect positional arguments
                for arg in node.args:
                    call_info['pos_args'].append(self._get_arg_value(arg))
                    
                # Collect keyword arguments
                for keyword in node.keywords:
                    call_info['kwargs'].append((keyword.arg, self._get_arg_value(keyword.value)))
                    
                self.calls[func_name].append(call_info)
            
            # Continue visiting child nodes
            self.generic_visit(node)
        
        def _get_func_name(self, node) -> str:
            if isinstance(node, ast.Name):
                return node.id
            elif isinstance(node, ast.Attribute):
                return node.attr
            return None
        
        def _get_arg_value(self, node) -> Union[str, int, float, bool, None]:
            if isinstance(node, ast.Name):
                return node.id
            elif isinstance(node, ast.Constant):
                return node.value
            elif isinstance(node, ast.Str):
                return node.s
            else:
                return ast.unparse(node)
    
        # Visit the AST and collect function calls
    visitor = FunctionCallVisitor()
    visitor.visit(tree)
    
    return visitor.calls

def map_params_to_nodes(func: Callable) -> Dict[str, Node]:
    """
    Dynamically map parameters to Node types based on how they're used in function calls.
    """
    function_calls = extract_function_calls(func)
    param_to_node = {}
    

    
    # For each function call, map its arguments to the corresponding Node
    for func_name, calls in function_calls.items():
        if func_name in func_to_node:
            node_type = func_to_node[func_name]
            for call_args in calls:
                for param_name in call_args.values():
                    param_to_node[param_name] = node_type
    
    return param_to_node

def parse_values(func: Callable) -> Dict:
    """
    Parse a function to extract non-default values dynamically.
    
    Args:
        func (Callable): The function to parse
    
    Returns:
        Dict: A dictionary containing non-default values organized by Node type
    """
    # Get function signature
    signature = inspect.signature(func)
    
    # Extract default values from function parameters
    default_values = {
        param.name: param.default
        for param in signature.parameters.values()
        if param.default is not inspect.Parameter.empty
    }

    # print("default values", default_values)
    
    # # Get parameter to Node mapping
    # param_to_node = map_params_to_nodes(func)
    
    # # Initialize the non_default_values dictionary
    # non_default_values = {}
    
    # # Build node call index counter
    # node_indices = {}
    
    # Process function calls to determine the order of operations
    function_calls = extract_function_calls(func)

    # print("function calls")
    # debug(function_calls)
