import ast
import inspect
import logging
from io import StringIO
from textwrap import dedent
from typing import Callable, Dict, List, Optional

from devtools import debug
from pipeline_ui.modules.testing.testing_var import TESTING
from pydantic import BaseModel

from pipeline_ui.modules.node.schema.node_schema import NodeSchema
from pipeline_ui.modules.workflow.pretty_logger import PrettyLogger
from pipeline_ui.modules.workflow.schema.internal.schema import EdgeSource, EdgeTarget, WorkflowEdge


class VariableSource(BaseModel):
    node: str
    node_index: int
    output_index: int

class OutputMapping(BaseModel):
    func_name: str
    outputs: Dict[Optional[int], str]

def extract_edges_from_workflow(workflow_func: Callable, nodes: List[NodeSchema]) -> List[WorkflowEdge]:
    """
    Extract edges from a workflow function by analyzing its AST and tracing data flow.
    Handles both keyword and positional arguments.
    """
    logger = PrettyLogger(__name__, level=logging.INFO)

    # Create mappings from the node schemas
    func_name_to_node_name_mapping: Dict[str, str] = {node.func_name: node.name for node in nodes}
    
    # Create output and input mappings
    output_mapping = {}
    input_mapping = {}
    for node in nodes:
        # Map outputs
        output_mapping[node.func_name] = OutputMapping(
            func_name=node.func_name,
            outputs={i: output.name.lower() for i, output in enumerate(node.outputs)}
        )
        if len(node.outputs) == 1:
            output_mapping[node.func_name].outputs[None] = node.outputs[0].name.lower()
            
        # Map inputs
        input_mapping[node.func_name] = {i: input.name for i, input in enumerate(node.inputs)}

    source = inspect.getsource(workflow_func)

    if TESTING:
        source = dedent(source)
    
    tree = ast.parse(source)
    var_sources: Dict[str, VariableSource] = {}
    edges: List[WorkflowEdge] = []
    number_of_calls_per_func: Dict[str, int] = {}

    class EdgeExtractor(ast.NodeVisitor):
        def visit_Assign(self, node):
            if isinstance(node.value, ast.Call):
                logger.debug("\033[92massign\033[0m %s", ast.unparse(node))
                call_node: ast.Call = node.value

                if isinstance(call_node.func, ast.Name):
                    func_name = call_node.func.id
                else:
                    raise ValueError("Only direct function calls are supported, not method calls")

                logger.debug("assign number of calls %s %s", func_name, number_of_calls_per_func.get(func_name, 0))

                # Handle tuple unpacking
                if isinstance(node.targets[0], ast.Tuple):
                    for idx, target in enumerate(node.targets[0].elts):
                        if isinstance(target, ast.Name):
                            var_name = target.id
                            var_sources[var_name] = VariableSource(
                                node=func_name,
                                output_index=idx,
                                node_index=number_of_calls_per_func.get(func_name, 0)
                            )
                else:
                    # Handle single assignment
                    if isinstance(node.targets[0], ast.Name):
                        var_name = node.targets[0].id
                        var_sources[var_name] = VariableSource(
                            node=func_name,
                            output_index=0,
                            node_index=number_of_calls_per_func.get(func_name, 0)
                        )

                self.generic_visit(node)

        def visit_Call(self, node):
            if isinstance(node.func, ast.Name):
                logger.debug("\033[91mcall\033[0m %s", ast.unparse(node))

                target_func_name = node.func.id
                add_to_number_of_calls_per_func = True

                # Process positional arguments
                for arg_idx, arg in enumerate(node.args):
                    if isinstance(arg, ast.Name) and arg.id in var_sources:
                        if add_to_number_of_calls_per_func:
                            number_of_calls_per_func[target_func_name] = number_of_calls_per_func.get(target_func_name, 0) + 1
                            add_to_number_of_calls_per_func = False

                        source = var_sources[arg.id]
                        source_func = source.node
                        
                        # Get input name from mapping or use positional index
                        input_name = input_mapping.get(target_func_name, {}).get(arg_idx, f"input_{arg_idx}")
                        

                        print(f"[DEBUG] func_name_to_node_name_mapping: {func_name_to_node_name_mapping}")
                        edge = WorkflowEdge(
                            source=EdgeSource(
                                node=func_name_to_node_name_mapping[source_func],
                                output=output_mapping[source_func].outputs[source.output_index],
                                node_index=source.node_index
                            ),
                            target=EdgeTarget(
                                node=func_name_to_node_name_mapping[target_func_name],
                                input=input_name,
                                node_index=number_of_calls_per_func[target_func_name] - 1
                            )
                        )
                        
                        logger.debug("constructing edge %s", edge)
                        edges.append(edge)

                # Process keyword arguments
                for arg in node.keywords:
                    if arg.arg is None:
                        raise ValueError("all function arguments must be named")

                    if isinstance(arg.value, ast.Name) and arg.value.id in var_sources:
                        if add_to_number_of_calls_per_func:
                            number_of_calls_per_func[target_func_name] = number_of_calls_per_func.get(target_func_name, 0) + 1
                            add_to_number_of_calls_per_func = False

                        source = var_sources[arg.value.id]
                        source_func = source.node

                        edge = WorkflowEdge(
                            source=EdgeSource(
                                node=func_name_to_node_name_mapping[source_func],
                                output=output_mapping[source_func].outputs[source.output_index],
                                node_index=source.node_index
                            ),
                            target=EdgeTarget(
                                node=func_name_to_node_name_mapping[target_func_name],
                                input=arg.arg,
                                node_index=number_of_calls_per_func[target_func_name] - 1
                            )
                        )
                        
                        logger.debug("constructing edge %s", edge)
                        edges.append(edge)

            self.generic_visit(node)

        def remove_uncessary_indices(self):
            node_names_with_necessary_indices = {
                func_name_to_node_name_mapping[func_name]
                for func_name, number_of_calls in number_of_calls_per_func.items()
                if number_of_calls > 1
            }

            logger.debug("node_names_with_necessary_indices %s", node_names_with_necessary_indices)

            
            for edge in edges:
                edge.source.node_index = (
                    edge.source.node_index 
                    if edge.source.node in node_names_with_necessary_indices 
                    else None
                )
                edge.target.node_index = (
                    edge.target.node_index 
                    if edge.target.node in node_names_with_necessary_indices 
                    else None
                )

    extractor = EdgeExtractor()
    extractor.visit(tree)
    extractor.remove_uncessary_indices()

    

    logger.debug_obj(var_sources, "var_sources:")
    logger.debug_obj(edges, "edges:")
    logger.debug("number of edges %s", len(edges))

    for edge in edges:
        logger.debug("edge %s", edge)

    return edges