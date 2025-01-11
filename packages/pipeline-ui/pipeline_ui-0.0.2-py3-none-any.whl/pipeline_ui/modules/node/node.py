from typing import Callable, Dict, List, Optional

from pipeline_ui.modules.common_parser.full_code_extractor import get_full_code_for_node
from pipeline_ui.modules.common_parser.function_parser_extractor import FunctionInfo, extract_function_code_recursive
from pipeline_ui.modules.node._instance.parameter.schema import ParameterInstanceType

from .parser.get_method_args import get_method_args
from .parser.node_input_parser import get_node_inputs
from .parser.node_output_parser import get_node_outputs
from .parser.parameter_parser import get_parameters
from .schema.node_schema import (
    NodeInputInstance,
    NodeOutputInstance,
    NodeSchema,
)


class Node:
    def __init__(
        self,
        func: Callable,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ):
        self.func: Callable = func
        
        self.name: str = name or func.__name__.replace(" ", "_").lower()
        self.func_name: str = func.__name__
        self.description: str = description or ""
        self.docstring: Optional[str] = func.__doc__
        # self._default_values: Dict[str, Any] = self.get_default_values(func)

        self.inputs: List[NodeInputInstance] = get_node_inputs(func)
        self.outputs: List[NodeOutputInstance] = get_node_outputs(func)
        self.parameters: List[ParameterInstanceType] = get_parameters(func)
        # self.stream_func: Callable = get_stream_function(func)
        number_of_args = len(get_method_args(func))
        assert number_of_args == len(self.inputs) + len(self.parameters), f"Number of arguments in the function {func.__name__} does not match the number of inputs and parameters, expected {number_of_args}, got {len(self.inputs) + len(self.parameters)}"
        # print(self.to_schema().model_dump_json(indent=4))

        self.function_info: Dict[str, FunctionInfo] = extract_function_code_recursive(func, recursive=False)
        self.source_code = get_full_code_for_node(self.func_name, self.function_info)

    # def get_default_values(self, func: Callable) -> Dict[str, Any]:
    #     """Retrieve default values of function parameters."""
    #     signature = inspect.signature(func)
    #     return {k: v.default for k, v in signature.parameters.items() if v.default is not inspect.Parameter.empty}

    def __repr__(self) -> str:
        return f"Node(name: {self.name}, node_inputs: {self.inputs}, node_outputs: {self.outputs})"

    def to_schema(self) -> NodeSchema:
        """Convert node to a Pydantic model"""
        # print("parameters", self.parameters)
        return NodeSchema(
            name=self.name,
            func_name=self.func_name,
            description=self.description,
            docstring=self.docstring,
            inputs=self.inputs,
            outputs=self.outputs,
            parameters=self.parameters,
            function_info=self.function_info,
            source_code=self.source_code,
        )
    
    def to_json(self, published_pack_id: str) -> dict:
        json_data = self.to_schema().model_dump()
        json_data["pack_id"] = published_pack_id
        return json_data
