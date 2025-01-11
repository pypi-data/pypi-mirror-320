from dataclasses import dataclass
from typing import Dict, List

from pipeline_ui.modules.common_parser.function_parser_extractor import FunctionInfo
from pipeline_ui.modules.common_parser.import_merger import ImportMerger


def get_full_code_for_node(node_func_name: str, function_infos: Dict[str, FunctionInfo]) -> str: 
    assert len(function_infos) == 1, f"function_infos for node {node_func_name} should contain only one function for a node, got {len(function_infos)}, function_infos_keys: {function_infos.keys()}"
    imports = function_infos[node_func_name].imports
    source = function_infos[node_func_name].source_code

    merger = ImportMerger()
    import_str = merger.merge(imports)
    full_source = import_str + "\n\n" + source
    # print("full_source", full_source)
    # if node_func_name == "load_model":
    #     raise Exception("here")
    return full_source

@dataclass
class FullCode:
    imports: List[str]
    source_codes: List[str]

def build_source_code(from_function: str, function_infos: List[FunctionInfo]) -> FullCode:
    """
    Build source code from a list of FunctionInfo objects, starting from a specified function.
    
    Args:
        from_function: Name of the starting function
        function_infos: List of FunctionInfo objects containing function details
    
    Returns:
        str: Combined source code with dependencies ordered correctly
    """
    # Create a mapping of function names to their info for easy lookup
    function_map = {info.name: info for info in function_infos}
    
    # Keep track of processed functions to avoid duplicates
    processed = set()
    ordered_code = []
    imports = []
    
    def add_function_and_deps(func_name: str):
        if func_name in processed:
            return
        
        func_info = function_map.get(func_name)
        if not func_info:
            return
            
        # First process dependencies
        for called_func in func_info.called_functions:
            if called_func in function_map:
                add_function_and_deps(called_func)
        
        # Then add this function if not already processed
        if func_name not in processed:
            ordered_code.append(func_info.source_code)
            imports.extend(func_info.imports)
            processed.add(func_name)
    
    # Start building from the specified function
    add_function_and_deps(from_function)
    
    # Return the combined source code
    return FullCode(imports=imports, source_codes=ordered_code)

def get_full_code_for_workflow(workflow_func_name: str, function_infos: Dict[str, FunctionInfo]) -> str:
    full_code = build_source_code(workflow_func_name, list(function_infos.values()))

    merger = ImportMerger()
    import_str = merger.merge(full_code.imports)
    full_source = f"""
{import_str}


pui = PipelineUI()

{'\n\n'.join(full_code.source_codes)}

pui.run()
"""
    return full_source
