import ast
import inspect
from typing import Callable, List

from pipeline_ui.modules.node._instance.media_schema import (
    AudioInputInstance,
    FileInputInstance,
    ImageInputInstance,
    VideoInputInstance,
)
from pipeline_ui.modules.node._instance.schema import BaseNodeInputInstance, NodeInputInstance
from textwrap import dedent

from pipeline_ui.modules.testing.testing_var import TESTING


class NodeInputVisitor(ast.NodeVisitor):
    def __init__(self):
        self.node_inputs = {}
        
    def get_type_name(self, node: ast.AST) -> str:
        """Extract type name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            # Handle cases like Image.Image
            module_parts = []
            current = node
            while isinstance(current, ast.Attribute):
                module_parts.append(current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                module_parts.append(current.id)
            return ".".join(reversed(module_parts))
        return "Any"  # Default fallback

    def visit_FunctionDef(self, node: ast.FunctionDef):
        for arg in node.args.defaults:
            if isinstance(arg, ast.Call) and isinstance(arg.func, ast.Name) and arg.func.id == 'NodeInput':
                arg_name = node.args.args[len(node.args.args) - len(node.args.defaults) + node.args.defaults.index(arg)].arg
                input_type = arg.func.id
                
                param_info = {
                    'name': arg_name,
                    'python_type': None,
                    'description': None,
                    'input_type': input_type
                }
                
                for keyword in arg.keywords:
                    if keyword.arg == 'python_type':
                        param_info['python_type'] = self.get_type_name(keyword.value)
                    elif keyword.arg == 'description':
                        if isinstance(keyword.value, ast.Constant):
                            param_info['description'] = keyword.value.value
                
                self.node_inputs[arg_name] = param_info

            elif isinstance(arg, ast.Call) and isinstance(arg.func, ast.Name) and arg.func.id == 'ImageInput':
                arg_name = node.args.args[len(node.args.args) - len(node.args.defaults) + node.args.defaults.index(arg)].arg
                input_type = arg.func.id
                
                param_info = {
                    'name': arg_name,
                    'description': None,
                    'input_type': input_type,
                    'render': False,
                }

                for keyword in arg.keywords:
                    if keyword.arg == 'description':
                        if isinstance(keyword.value, ast.Constant):
                            param_info['description'] = keyword.value.value
                    if keyword.arg == 'render':
                        if isinstance(keyword.value, ast.Constant):
                            param_info['render'] = keyword.value.value
                
                self.node_inputs[arg_name] = param_info

def get_node_inputs(func: Callable) -> List[NodeInputInstance]:
    """
    Extract NodeInput parameters from a function using AST parsing.
    """
    try:
        source = inspect.getsource(func)
    except (IOError, TypeError):
        return []
    
    

    if TESTING:
        source = dedent(source)
    
    print("source\n", source)

    tree = ast.parse(source)
    
    visitor = NodeInputVisitor()
    visitor.visit(tree)
    
    nodes = []
    for param_info in visitor.node_inputs.values():
        input_type = param_info['input_type']
        # Get the appropriate input instance class

        # For ImageInputInstance, use the predefined python_type from schema
        if input_type == 'ImageInput':
            nodes.append(ImageInputInstance(
                name=param_info['name'],
                description=param_info['description'],
                color="purple",
                render=param_info['render']
            ))
        elif input_type == 'FileInput':
            nodes.append(FileInputInstance(
                name=param_info['name'],
                description=param_info['description'],
                color="purple"
            ))
        elif input_type == 'VideoInput':
            nodes.append(VideoInputInstance(
                name=param_info['name'],
                description=param_info['description'],
                color="purple"
            ))
        elif input_type == 'AudioInput':
            nodes.append(AudioInputInstance(
                name=param_info['name'],
                description=param_info['description'],
                color="purple"
            ))
        else:
            nodes.append(BaseNodeInputInstance(
                name=param_info['name'],
                description=param_info['description'],
                python_type=param_info['python_type'],
                color="purple"
            ))
    
    return nodes