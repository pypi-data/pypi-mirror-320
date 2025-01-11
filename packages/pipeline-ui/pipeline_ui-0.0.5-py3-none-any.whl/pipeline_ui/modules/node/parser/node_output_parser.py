from typing import Annotated, Callable, List, get_args, get_origin, get_type_hints

from pipeline_ui.modules.node._instance.base_schema import NodeOutputInstance
from pipeline_ui.modules.node._pin.base_schema import NodeOutput




def get_node_outputs(func: Callable) -> List[NodeOutputInstance]:
    """Extract NodeOutput annotations from function return type."""
    node_outputs = []
    hints = get_type_hints(func, include_extras=True)

    if "return" in hints:
        return_type = hints["return"]

        # Handle tuple return type
        if get_origin(return_type) is tuple:
            tuple_args = get_args(return_type)
            for type_arg in tuple_args:
                if get_origin(type_arg) is Annotated:
                    type_args = get_args(type_arg)
                    for arg in type_args:
                        if isinstance(arg, NodeOutput):
                            node_output_instance = NodeOutputInstance(
                                description=arg.description,
                                python_type=type_args[0].__name__,
                                name=arg.name,
                            )
                            node_outputs.append(node_output_instance)
                            break
        # Handle single return type
        elif get_origin(return_type) is Annotated:
            type_args = get_args(return_type)
            for arg in type_args:
                if isinstance(arg, NodeOutput):
                    node_output_instance = NodeOutputInstance(
                        description=arg.description,
                        python_type=type_args[0].__name__,
                        name=arg.name,
                    )
                    node_outputs.append(node_output_instance)
                    break

    return node_outputs