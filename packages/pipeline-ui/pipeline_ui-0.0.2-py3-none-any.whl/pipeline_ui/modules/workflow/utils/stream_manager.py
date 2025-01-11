import os
import shutil
from textwrap import dedent
import time
import uuid
from enum import Enum
from functools import wraps
from queue import Queue

from pipeline_ui.modules.beam.utils import is_running_on_beam
from pipeline_ui.modules.testing.testing_var import TESTING


class FuncType(Enum):
    NODE = "node"
    WORKFLOW = "workflow"

class StreamStateManager():
    """
    Manages the state of the workflow execution to capture the execution flow (time taken, etc.) of the workflow.
    """
    def __init__(self):
        self.state = {}
        self.output_queue = Queue()
        self.extra_start_state = {}
        self.extra_end_state = {}
        self.registered_funcs = set()
        self.completed_funcs = set()

    def register_start(self, func_name, func_type: FuncType):
        self.state[func_name] = time.time()
        self.registered_funcs.add(func_name)
        state_message = {
            "name": func_name,
            "status": "started", 
            "func_type": func_type.value
        }
        state_message.update(self.extra_start_state.get(func_name, {}))
        self.extra_start_state[func_name] = {}
        self.output_queue.put(state_message)

    def append_to_start(self, func_name, key, value):
        if func_name in self.registered_funcs:
            raise RuntimeError(f"Cannot append to start state after {func_name} has been registered")
        
        if func_name not in self.extra_start_state:
            self.extra_start_state[func_name] = {}

        self.extra_start_state[func_name][key] = value

    def append_to_end(self, func_name, key, value):
        if func_name in self.completed_funcs:
            raise RuntimeError(f"Cannot append to end state after {func_name} has completed")
            
        if func_name not in self.extra_end_state:
            self.extra_end_state[func_name] = {}
            
        self.extra_end_state[func_name][key] = value

    def reset_function_state(self, func_name):
        """Reset the state for a specific function to allow multiple runs"""
        if func_name in self.registered_funcs:
            self.registered_funcs.remove(func_name)
        if func_name in self.completed_funcs:
            self.completed_funcs.remove(func_name)
        if func_name in self.state:
            del self.state[func_name]
        if func_name in self.extra_start_state:
            self.extra_start_state[func_name] = {}
        if func_name in self.extra_end_state:
            self.extra_end_state[func_name] = {}

    def register_end(self, func_name, func_type: FuncType):
        end_time = time.time()
        duration = end_time - self.state[func_name]
        state_message = {
            "name": func_name,
            "status": "completed",
            "func_type": func_type.value,
            "duration": f"{duration:.2f}s"
        }
        state_message.update(self.extra_end_state.get(func_name, {}))
        self.extra_end_state[func_name] = {}
        self.output_queue.put(state_message)
        self.completed_funcs.add(func_name)
        # if func_type == FuncType.WORKFLOW:
        self.reset_function_state(func_name)



def stream_wrapper(func, stream_state_manager: StreamStateManager, func_type: FuncType):
    @wraps(func)
    def wrapper(*args, **kwargs):  # Add *args, **kwargs to accept any arguments
        stream_state_manager.register_start(func.__name__, func_type)
        print("stream_wrapper", func.__name__)
        result = func(*args, **kwargs)  # Pass the arguments to the wrapped function
        stream_state_manager.register_end(func.__name__, func_type)
        return result  # Return the result if any
    return wrapper

from typing import Any, Callable, Dict, List, Tuple
from inspect import signature, Parameter
import ast
from inspect import getsource
from typing import List

def get_rendered_image_inputs(func: Callable) -> List[str]:
    """
    Analyzes a function to find parameters that use ImageInput with render=True.
    Returns list of parameter names.
    so would return ["image"] for the following function:
    def my_function(image: ImageInput = ImageInput(render=True)):
        ...
    """
    # Get function source code
    source = getsource(func)

    if TESTING:
        source = dedent(source)
    
    # Parse the source into an AST
    tree = ast.parse(source)
    
    rendered_params = []
    
    # Visit all function definitions
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # Look at each argument's default value
            for arg in node.args.defaults:
                if isinstance(arg, ast.Call):
                    # Check if it's an ImageInput call
                    if getattr(arg.func, 'id', None) == 'ImageInput':
                        # Look for render=True in the keywords
                        for keyword in arg.keywords:
                            if (keyword.arg == 'render' and 
                                isinstance(keyword.value, ast.Constant) and 
                                keyword.value.value is True):
                                # Find the corresponding parameter name
                                idx = node.args.defaults.index(arg)
                                param_name = node.args.args[-(len(node.args.defaults) - idx)]
                                rendered_params.append(param_name.arg)
    
    return rendered_params

def get_rendered_image_outputs(func: Callable) -> List[str]:
    """
    Analyzes a function to find return annotations that use ImageOutput with render=True.
    Returns list of output names.
    """
    source = getsource(func)


    if TESTING:
        source = dedent(source)

    tree = ast.parse(source)
    rendered_outputs = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # Check if there's a return annotation
            if node.returns:
                # Look for Annotated type with ImageOutput
                if isinstance(node.returns, ast.Subscript):
                    if getattr(node.returns.value, 'id', None) == 'Annotated':
                        # Get the second argument which should be ImageOutput
                        image_output = node.returns.slice.elts[1]
                        if isinstance(image_output, ast.Call) and getattr(image_output.func, 'id', None) == 'ImageOutput':
                            # Check for render=True in keywords
                            for keyword in image_output.keywords:
                                if (keyword.arg == 'render' and 
                                    isinstance(keyword.value, ast.Constant) and 
                                    keyword.value.value is True):
                                    # Get the name from the ImageOutput arguments
                                    for kw in image_output.keywords:
                                        if kw.arg == 'name':
                                            rendered_outputs.append(kw.value.value)
                                            break
    
    return rendered_outputs

from PIL import Image
import inspect

class RenderManager():
    """
    Manages the rendering of artifacts.
    """
    def __init__(self):
        self.artifacts = {} # artifact_id -> artifact_path
        self.artifact_path = os.path.join(os.path.expanduser("~"), ".cache", "pipeline-ui", "artifacts")
        # empty the directory
        shutil.rmtree(self.artifact_path, ignore_errors=True)
        os.makedirs(self.artifact_path, exist_ok=True)

    def add_artifact_from_input(self, func: Callable, args: Tuple[Any], kwargs: Dict[str, Any], stream_state_manager: StreamStateManager):
        rendered_params = get_rendered_image_inputs(func)

        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()
        parameters = bound_args.arguments

        for rendered_param in rendered_params:
            if rendered_param in parameters:
                image : Image.Image = parameters[rendered_param]
                assert isinstance(image, Image.Image), f"Expected Image.Image, got {type(image)}"
                artifact_id = str(uuid.uuid4())
                artifact_path = os.path.join(self.artifact_path, f"{artifact_id}.png")
                image.save(artifact_path)

                # save the value in the path ~/.cache/pipeline-ui/artifacts/<artifact_id>
                self.artifacts[artifact_id] = artifact_path
                stream_state_manager.append_to_start(func.__name__, "artifact_id", artifact_id)

                if is_running_on_beam():
                    from beam import Output
                    if not os.path.exists(artifact_path):
                        raise RuntimeError(f"Artifact file {artifact_path} does not exist")
                    try:
                        with open(artifact_path, 'rb') as f:
                            # Try reading first few bytes to check if file is corrupt
                            f.read(1024)
                    except IOError as e:
                        raise RuntimeError(f"Artifact file {artifact_path} is corrupt: {str(e)}")

                    output_file = Output(path=artifact_path)
                    output_file.save()
                    public_url = output_file.public_url(expires=3600)
                    stream_state_manager.append_to_start(func.__name__, "artifact_url", public_url)
                else:
                    stream_state_manager.append_to_start(func.__name__, "artifact_url", f"http://localhost:8114/api/workflows/artifacts/{artifact_id}")

    def add_artifact_from_output(self, func: Callable, output: Any, stream_state_manager: StreamStateManager):
        rendered_outputs = get_rendered_image_outputs(func)

        # print("rendered_outputs", rendered_outputs)
        
        if rendered_outputs and isinstance(output, Image.Image):
            # print("output", output)
            artifact_id = str(uuid.uuid4())
            artifact_path = os.path.join(self.artifact_path, f"{artifact_id}.png")
            output.save(artifact_path)
            # print("saved to", artifact_path)
            
            self.artifacts[artifact_id] = artifact_path
            stream_state_manager.append_to_end(func.__name__, "artifact_id", artifact_id)
            stream_state_manager.append_to_end(func.__name__, "artifact_url", f"localhost:8114/api/workflows/artifacts/{artifact_id}")
            stream_state_manager.append_to_end(func.__name__, "func_output", output)

def render_wrapper(func, stream_state_manager: StreamStateManager, render_manager: RenderManager):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print("render_wrapper", func.__name__)
        render_manager.add_artifact_from_input(func, args, kwargs, stream_state_manager)
        output = func(*args, **kwargs)
        render_manager.add_artifact_from_output(func, output, stream_state_manager)
        return output
    
    return wrapper
