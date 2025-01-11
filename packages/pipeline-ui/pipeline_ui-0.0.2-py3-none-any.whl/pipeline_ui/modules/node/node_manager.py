from typing import Callable, Dict, Optional
from pipeline_ui.modules.io_manager.io_manager import IORedirectManager, io_wrapper
from pipeline_ui.modules.node.node import Node
from pipeline_ui.modules.workflow.utils.stream_manager import (
    FuncType, 
    StreamStateManager, 
    RenderManager,
    stream_wrapper,
    render_wrapper
)

class NodeManager:
    def __init__(self, stream_state_manager: Optional[StreamStateManager] = None, 
                 render_manager: Optional[RenderManager] = None,
                 io_redirect_manager: Optional[IORedirectManager] = None):
        self.nodes: Dict[str, Node] = {}
        self.stream_state_manager = stream_state_manager
        self.render_manager = render_manager
        self.io_redirect_manager = io_redirect_manager

    def wrap_function(self, func: Callable) -> Callable:
        """Applies all necessary wrappers to a function"""
        wrapped_func = func
        
        if self.io_redirect_manager:
            wrapped_func = io_wrapper(wrapped_func, self.io_redirect_manager)
        
        if self.stream_state_manager and self.render_manager:
            wrapped_func = stream_wrapper(wrapped_func, self.stream_state_manager, FuncType.NODE)
            wrapped_func = render_wrapper(wrapped_func, self.stream_state_manager, self.render_manager)
        
        return wrapped_func

    def register_node(
        self,
        func: Callable,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Callable:
        """
        Decorator for creating a node.
        
        Args:
            name (Optional[str]): Optional custom name for the node
            description (Optional[str]): Optional description of the node's functionality
        
        Returns:
            Callable: A decorator function that registers the decorated function as a node
        """
        wrapped_func = self.wrap_function(func)
        self.add_node(wrapped_func, name, description)
        return wrapped_func


    def add_node(
        self,
        func: Callable,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ):
        """
        Add a node to the manager.
        
        Args:
            func (Callable): The function to be registered as a node
            name (Optional[str]): Optional custom name for the node
            description (Optional[str]): Optional description of the node's functionality
        """
        self.nodes[func.__name__] = Node(func, name, description)