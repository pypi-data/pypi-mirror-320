from typing import Callable, Dict, List, Optional
from pipeline_ui.modules.io_manager.io_manager import IORedirectManager, io_wrapper
from pipeline_ui.modules.workflow.workflow import Workflow
from pipeline_ui.modules.workflow.schema.client.schema import NodePosition
from pipeline_ui.modules.node.node import Node
from pipeline_ui.modules.workflow.utils.stream_manager import (
    FuncType,
    StreamStateManager,
    RenderManager,
    stream_wrapper,
    render_wrapper
)

class WorkflowManager:
    def __init__(
        self,
        nodes: Dict[str, Node],
        stream_state_manager: Optional[StreamStateManager] = None,
        render_manager: Optional[RenderManager] = None,
        io_redirect_manager: Optional[IORedirectManager] = None
    ):
        self.workflows: Dict[str, Workflow] = {}
        self.nodes = nodes
        self.stream_state_manager = stream_state_manager
        self.render_manager = render_manager
        self.io_redirect_manager = io_redirect_manager

    def wrap_function(self, func: Callable) -> Callable:
        wrapped_func = func

        if self.io_redirect_manager:
            wrapped_func = io_wrapper(wrapped_func, self.io_redirect_manager)

        if self.stream_state_manager and self.render_manager:
            wrapped_func = render_wrapper(wrapped_func, self.stream_state_manager, self.render_manager)
            wrapped_func = stream_wrapper(wrapped_func, self.stream_state_manager, FuncType.WORKFLOW)
        
        return wrapped_func

    def register_workflow(
        self,
        func: Callable,
        name: Optional[str] = None,
        description: Optional[str] = None,
        positions: Optional[List[NodePosition]] = None
    ) -> Callable:
        """
        Decorator for creating a workflow.
        
        Args:
            name (Optional[str]): Optional custom name for the workflow
            description (Optional[str]): Optional description for the workflow
            positions (Optional[List[NodePosition]]): Optional list of node positions in the UI
        
        Returns:
            Callable: A decorator function that registers the decorated function as a workflow
        """
        

        wrapped_func = self.wrap_function(func)
        # If no stream/render managers, just add the workflow directly
        self.add_workflow(wrapped_func, name, positions, description)
        return wrapped_func

    def add_workflow(
        self,
        func: Callable,
        name: Optional[str] = None,
        positions: Optional[List[NodePosition]] = None,
        description: Optional[str] = None,
    ):
        """
        Add a workflow to the manager.
        
        Args:
            func (Callable): The function to be registered as a workflow
            name (Optional[str]): Optional custom name for the workflow
            positions (Optional[List[NodePosition]]): Optional list of node positions in the UI
        """
        self.workflows[func.__name__] = Workflow(
            func=func,
            name=name,
            nodes=self.nodes,
            positions=positions
        )