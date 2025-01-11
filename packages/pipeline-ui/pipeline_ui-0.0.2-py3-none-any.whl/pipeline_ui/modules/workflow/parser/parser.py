import ast
import inspect
from typing import Callable, Dict, List

from pipeline_ui.modules.node.node import Node
from pipeline_ui.modules.node.schema.node_schema import NodeSchema
from pipeline_ui.modules.workflow.schema.internal.schema import EdgeSource, EdgeTarget, WorkflowEdge


def extract_workflow_edges(workflow_func) -> List[WorkflowEdge]:
    """Analyzes a workflow function and extracts edges by tracking variable assignments and usage."""
    import ast
    import inspect

    class EdgeExtractor(ast.NodeVisitor):
        def __init__(self):
            self.edges = []
            self.var_to_node = {}
            self.var_to_outputs = {}

        def visit_Assign(self, node):
            if isinstance(node.value, ast.Call):
                # Handle single assignment
                target_name = node.targets[0].id if isinstance(node.targets[0], ast.Name) else None
                self.handle_function_call(target_name, node.value)
            elif isinstance(node.value, ast.Tuple):
                # Handle multiple assignment (e.g., model, clip, vae = load_checkpoint())
                if isinstance(node.targets[0], ast.Tuple):
                    target_names = [t.id for t in node.targets[0].elts if isinstance(t, ast.Name)]
                    if isinstance(node.value, ast.Call):
                        for i, name in enumerate(target_names):
                            self.var_to_outputs[name] = {
                                "node": node.value.func.id,
                                "output_index": i,
                            }

        def handle_function_call(self, target_name, call_node):
            if isinstance(call_node.func, ast.Name):
                func_name = call_node.func.id
                # Track what variable stores which node's output
                if target_name:
                    self.var_to_node[target_name] = func_name

                # Analyze function arguments to build edges
                for kw in call_node.keywords:
                    arg_name = kw.arg
                    if isinstance(kw.value, ast.Name) and kw.value.id in self.var_to_node:
                        source_var = kw.value.id
                        source_node = self.var_to_node.get(source_var)
                        if source_node:
                            # If this variable is from a multi-output node
                            if source_var in self.var_to_outputs:
                                output_info = self.var_to_outputs[source_var]
                                source_node = output_info["node"]
                                # Map output_index to actual output name based on node definition
                                output_name = output_info.get("output_name", "output")
                            else:
                                output_name = "output"

                            self.edges.append(
                                WorkflowEdge(
                                    source=EdgeSource(node=source_node, output=output_name),
                                    target=EdgeTarget(node=func_name, input=arg_name),
                                )
                            )

    # Get function source and parse
    source = inspect.getsource(workflow_func)
    tree = ast.parse(source)

    # Extract edges
    extractor = EdgeExtractor()
    extractor.visit(tree)

    return extractor.edges

def extract_nodes(func: Callable, nodes: Dict[str, Node]) -> List[NodeSchema]:
    nodes_names = nodes.keys()


    print("nodes_names", nodes_names)

    # TODO dirty hack to remove the ImageOutput
    nodes_names = [node_name for node_name in nodes_names if node_name != func.__name__]

    # print("nodes_names", nodes_names)
    # print("nodes[node_name]", [nodes[node_name] for node_name in nodes_names])
    try:
        return [nodes[node_name].to_schema() for node_name in nodes_names]
    except NameError as e:
        print("NameError", e)
        raise e
