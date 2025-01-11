import ast
import inspect
from textwrap import dedent
from typing import Callable, List

from pipeline_ui.modules.node._instance.common_schema import (
    NumberParameterInstance,
    RadioParameterInstance,
    TextParameterInstance,
)
from pipeline_ui.modules.node._instance.media_schema import (
    AudioParameterInstance,
    FileParameterInstance,
    ImageParameterInstance,
    VideoParameterInstance,
)
from pipeline_ui.modules.node._instance.parameter.schema import ParameterInstanceType
from pipeline_ui.modules.node._parameter.schema import ParameterType
from pipeline_ui.modules.testing.testing_var import TESTING

PARAMETER_TYPES = ['NumberParameter', 'RadioParameter', 'TextParameter', 'ImageParameter', 'AudioParameter', 'VideoParameter', 'FileParameter']
assert len(PARAMETER_TYPES) == len(ParameterType.__args__), f"the number of parameter types must match the number of parameter types in ParameterType, got {PARAMETER_TYPES} expected {len(ParameterType.__args__)}"

class ParameterVisitor(ast.NodeVisitor):
    def __init__(self):
        self.parameters = {}
        
    def visit_FunctionDef(self, node: ast.FunctionDef):
        for arg in node.args.defaults:
            if isinstance(arg, ast.Call) and isinstance(arg.func, ast.Name):
                # Get the parameter name from the arguments
                arg_name = node.args.args[len(node.args.args) - len(node.args.defaults) + node.args.defaults.index(arg)].arg
                                
                if arg.func.id in PARAMETER_TYPES:
                    param_info = {
                        'name': arg_name,
                        'description': None,
                        'default': None
                    }
                    
                    # Extract information from the Parameter arguments
                    for keyword in arg.keywords:
                        if keyword.arg == 'description' and isinstance(keyword.value, ast.Constant):
                            param_info['description'] = keyword.value.value
                        elif keyword.arg == 'default' and isinstance(keyword.value, (ast.Constant, ast.Num)):
                            param_info['default'] = keyword.value.value
                        elif keyword.arg == 'min' and isinstance(keyword.value, (ast.Constant, ast.Num)):
                            param_info['min'] = keyword.value.value
                        elif keyword.arg == 'max' and isinstance(keyword.value, (ast.Constant, ast.Num)):
                            param_info['max'] = keyword.value.value
                        elif keyword.arg == 'options' and isinstance(keyword.value, ast.List):
                            param_info['options'] = [
                                elem.value for elem in keyword.value.elts 
                                if isinstance(elem, ast.Constant)
                            ]
                    
                    # Store with parameter type
                    param_info['type'] = arg.func.id
                    self.parameters[arg_name] = param_info

def get_parameters(func: Callable) -> List[ParameterInstanceType]:
    """
    Extract Parameter information from a function using AST parsing.
    
    Args:
        func: The function to analyze
    
    Returns:
        List of Parameter instances (Number, Radio, or Text) containing parameter properties
    """
    # Get the source code
    try:
        source = inspect.getsource(func)
    except (IOError, TypeError):
        return []
    
    if TESTING:
        source = dedent(source)

    # Parse the source code into an AST
    tree = ast.parse(source)
    
    # Visit the AST and collect Parameter information
    visitor = ParameterVisitor()
    visitor.visit(tree)
    
    # Convert the collected information to appropriate Parameter instances
    parameters = []
    for param_info in visitor.parameters.values():
        if param_info['type'] == 'NumberParameter':
            print("param_info", param_info)
            python_type = 'int' if isinstance(param_info['default'], int) else 'float'
            parameters.append(NumberParameterInstance(
                name=param_info['name'],
                description=param_info['description'],
                default=param_info['default'],
                min=param_info.get('min'),
                max=param_info.get('max'),
                python_type=python_type
            ))
        elif param_info['type'] == 'RadioParameter':
            parameters.append(RadioParameterInstance(
                name=param_info['name'],
                description=param_info['description'],
                default=param_info['default'],
                options=param_info.get('options', []),

            ))
        elif param_info['type'] == 'TextParameter':
            assert isinstance(param_info['default'], str), "TextParameter default must be a string"
            assert isinstance(param_info['description'], str), "TextParameter description must be a string"
            assert isinstance(param_info['name'], str), "TextParameter name must be a string"
            parameters.append(TextParameterInstance(
                name=param_info['name'],
                description=param_info['description'],
                default=param_info['default'],
            ))
        elif param_info['type'] == 'ImageParameter':
            parameters.append(ImageParameterInstance(
                description=param_info['description'],
            ))
        elif param_info['type'] == 'AudioParameter':
            parameters.append(AudioParameterInstance(
                description=param_info['description'],
            ))
        elif param_info['type'] == 'VideoParameter':
            parameters.append(VideoParameterInstance(
                description=param_info['description'],
            ))
        elif param_info['type'] == 'FileParameter':
            parameters.append(FileParameterInstance(
                description=param_info['description'],
            ))
        else:
            raise ValueError(f"Unknown parameter type: {param_info['type']}")
    
    return parameters