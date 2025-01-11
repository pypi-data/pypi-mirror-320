def validate_code(code: str) -> None:
    # assert len(function_infos) == 1, f"function_infos should contain only one function for a node, got {len(function_infos)}, function_infos_keys: {function_infos.keys()}"

    # check that all functionInfo are node or workflow, no side methods

    # check all variables are defined in the code in the workflow or node so position outside workflow would not get validated
    # calling function outside workflow or node would not get validated (so get_device()) would lead to no validation
    ... 
