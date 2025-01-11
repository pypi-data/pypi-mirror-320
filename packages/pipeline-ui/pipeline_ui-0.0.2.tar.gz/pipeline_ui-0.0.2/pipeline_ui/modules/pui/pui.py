import os
from pathlib import Path
from typing import Callable, Dict, List, Optional

from fastapi.testclient import TestClient
from pipeline_ui.modules.io_manager.io_manager import IORedirectManager
from pipeline_ui.modules.node.node_manager import NodeManager
from pipeline_ui.modules.pack.pack import Pack
from pipeline_ui.modules.pui.auto_loader import ModuleAutoloader
from pipeline_ui.modules.workflow.workflow_manager import WorkflowManager
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from pipeline_ui.modules.node.node import Node
from pipeline_ui.modules.workflow.schema.client.schema import NodePosition
from pipeline_ui.modules.workflow.utils.stream_manager import FuncType, RenderManager, StreamStateManager, render_wrapper, stream_wrapper
from pipeline_ui.modules.workflow.workflow import Workflow


class PipelineUI():

    _nodes: Dict[str, Dict] = {}
    _workflows: Dict[str, Dict] = {}
    _instance = None  # Keep track of the current instance


    def __init__(self, host: str = "127.0.0.1", port: int = 8114):
        self.host: str = host
        self.port: int = port
        self.stream_state_manager = StreamStateManager()
        self.render_manager = RenderManager()
        self.io_redirect_manager = IORedirectManager() if self.get_io_redirect_state() else None
        if self.io_redirect_manager is not None:
            print(f"IO redirect manager enabled: {self.io_redirect_manager is not None}")
            print(f"IO redirect manager: {self.io_redirect_manager}")

        self.node_manager = NodeManager(
            self.stream_state_manager, 
            self.render_manager, 
            self.io_redirect_manager
        )
        self.workflow_manager = WorkflowManager(
            nodes=self.node_manager.nodes,
            stream_state_manager=self.stream_state_manager,
            render_manager=self.render_manager,
            io_redirect_manager=self.io_redirect_manager
        )
        self.pack = None
        self.autoloader = ModuleAutoloader()
        PipelineUI._instance = self
        
        
        # print("PipelineUI initialized")

    @classmethod
    def register_node(cls, func: Callable, name: Optional[str] = None, description: Optional[str] = None) -> Callable:
        """Store a node function for later registration, the behavior of the function is not changed until the PipelineUI is initialized"""
        if cls._instance is None:
            raise Exception(
                "PipelineUI is not initialized.\n"
                "You first need to initialize PipelineUI before using the @node decorator.\n"
                "The correct order is:\n"
                "1. pui = PipelineUI()\n"
                "2. @node()\n"
                "(You are doing it the other way around)"
            )  
            # If PipelineUI is already initialized, register directly with NodeManager
        return cls._instance.node_manager.register_node(func, name=name, description=description)

            
    
    @classmethod
    def register_workflow(cls, func: Callable, name: Optional[str] = None, 
                         description: Optional[str] = None, 
                         positions: Optional[List[NodePosition]] = None) -> Callable:
        """Store a workflow function for later registration, the behavior of the function is not changed until the PipelineUI is initialized"""
        if cls._instance is None:
            raise Exception(
                "PipelineUI is not initialized.\n"
                "You first need to initialize PipelineUI before using the @workflow decorator.\n"
                "The correct order is:\n"
                "1. pui = PipelineUI()\n"
                "2. @workflow()\n"
                "(You are doing it the other way around)"
            )  

        # If PipelineUI is already initialized, register directly
        return cls._instance.workflow_manager.register_workflow(func=func, name=name, description=description, positions=positions)
        
            
    
    def _register_discovered_components(self):
        """Register all discovered nodes and workflows with this instance
        When the PipelineUI is initialized, this method changes the behavior of the underlying functions so that the pipeline ui logic is applied
        """
        # Register nodes using the original node() method
        for node_info in self._nodes.values():


             # Get the original function from globals
            original_func = globals().get(node_info['func'].__name__)
            if original_func:
                print(f"[DEBUG] Global func ID: {id(original_func)} for {node_info['func'].__name__}")

            new_func = self.node_manager.register_node(
                func=node_info['func'],
                name=node_info['name'],
                description=node_info['description']
            )
            # def dummy_func():
            #     raise Exception("stop1")
            # node_info['func'] = new_func
            globals()[node_info['func'].__name__] = new_func
            print(f"[DEBUG] Updated global func ID: {id(globals()[node_info['func'].__name__])} for {node_info['func'].__name__}")
            node_info['func'] = new_func
        
        # Register workflows using the original workflow() method
        for workflow_info in self._workflows.values():
            new_func = self.workflow_manager.register_workflow(
                func=workflow_info['func'],
                name=workflow_info['name'],
                description=workflow_info['description'],
                positions=workflow_info['positions']
            )
            # def dummy_func():
            #     raise Exception("stop2")
            # workflow_info['func'] = new_func
            globals()[workflow_info['func'].__name__] = new_func

        # Clear the class-level storage since everything is now registered
        self._nodes.clear()
        self._workflows.clear()

    def get_io_redirect_state(self) -> bool:
        return False

    def define_pack(self, name: str, description: str) -> Pack:
        self.pack = Pack(name, description)
        return self.pack
    
    # def _start_server(self) -> None:
    
    def start(self, testing: bool = False):
        """
        Start the FastAPI server. The server is created in the `server.py` file and
        receives the current PipelineUI instance.
        """
        print(f"Starting Pipeline UI server on {self.host}:{self.port}")


        self._auto_load_modules()
        self._register_discovered_components()



        from pipeline_ui.modules.docs.router import router as docs_router
        from pipeline_ui.modules.node.router import router as node_router
        from pipeline_ui.modules.workflow.router import router as workflow_router

        app = FastAPI()

        app.state.pui = self

        # Middleware setup (e.g., CORS)
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[
                "http://localhost:5173", 
                "http://localhost:5174", 
                "http://127.0.0.1:8114",
            ],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Include node and workflow routers, passing the PipelineUI instance
        app.include_router(node_router, tags=["nodes"])
        app.include_router(workflow_router, tags=["workflows"])
        app.include_router(docs_router, tags=["docs"])

        # static_files_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "static")
        # app.mount("/", StaticFiles(directory=static_files_dir, html=True), name="static")

        DISABLE_UI = os.getenv("DISABLE_UI", "False") == "True"
        # print(f"[DEBUG] DISABLE_UI value: {DISABLE_UI}, type: {type(DISABLE_UI)}")

        if DISABLE_UI:
            @app.get("/")
            async def redirect_to_docs():
                return RedirectResponse(url="/docs")
            
            print(f"[DEBUG] ui has been disabled")
        else:
            PIPELINE_UI_DIR = Path(__file__).parent.parent.parent
            static_files_dir = PIPELINE_UI_DIR / "static"
            app.mount("/", StaticFiles(directory=static_files_dir, html=True), name="static")
        
        
        if testing:
            return TestClient(app)
        else:
            uvicorn.run(app, host=self.host, port=self.port)



    @property
    def nodes(self) -> Dict[str, Node]:
        return self.node_manager.nodes

    @property
    def workflows(self) -> Dict[str, Workflow]:
        return self.workflow_manager.workflows
    
    def _auto_load_modules(self):
        """Auto-load modules containing node and workflow decorators"""
        print("Auto-loading modules...")
        import sys
        
        # Get the directory of the main script
        main_script = os.path.abspath(sys.argv[0])
        base_dir = os.path.dirname(main_script)
        
        # Create autoloader and scan for modules
        self.autoloader.scan_directory_for_pui(base_dir, subdirs=['node', 'workflow'])


# Create decorators that use PipelineUI's class methods
def node(*, name: Optional[str] = None, description: Optional[str] = None):
    """
        Decorator for creating a node in the Pipeline UI.\n
        \n
        This decorator is used to mark a function as a node in the pipeline.\n
        It registers the function with the PipelineUI instance and creates a Node object.\n
        \n
        Args:\n
            output_names (Optional[List[str]]): An optional list of names for the node's outputs.\n
                If provided, these names will be used to label the outputs in the UI.\n
                If not provided, default names will be used.\n
        \n
        Returns:\n
            Callable: A decorator function that registers the decorated function as a node.\n
        \n
        Example:\n
            @node(output_names=["sum", "product"])\n
            def math_operations(a: int, b: int) -> Tuple[int, int]:\n
                return a + b, a * b\n
        """
    def decorator(func: Callable) -> Callable:
        return PipelineUI.register_node(func, name=name, description=description)
    return decorator

def workflow(*, name: Optional[str] = None, description: Optional[str] = None, 
             positions: Optional[List[NodePosition]] = None):
    """
        Decorator for creating a workflow in the Pipeline UI.

        This decorator is used to mark a function as a workflow in the pipeline.
        It registers the function with the PipelineUI instance and creates a Workflow object.

        Returns:
            Callable: A decorator function that registers the decorated function as a workflow.

        Example:
            @workflow()
            def my_workflow(param1: int, param2: str):
                # Workflow logic here
                pass
        """
    def decorator(func: Callable) -> Callable:
        return PipelineUI.register_workflow(func, name=name, description=description, 
                                          positions=positions)
    return decorator