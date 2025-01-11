# import ast
# from typing import Set


# def create_ast_from_str(code_str: str) -> ast.AST:
#     """Create an AST node from a string of Python code"""
#     tree = ast.parse(code_str)
#     return tree.body[0]

# class NodeStreamerTransformer(ast.NodeTransformer):
#     """Transform functions to include yield statements for progress reporting"""
    
#     def __init__(self, func_name: str, streaming_funcs: Set[str]):
#         self.func_name = func_name
#         self.streaming_funcs = streaming_funcs
#         self.lineno = 1
#         self.temp_var_counter = 0

#     def get_temp_var(self) -> str:
#         """Generate unique temporary variable names"""
#         self.temp_var_counter += 1
#         return f'_tmp_{self.temp_var_counter}'

#     def create_timing_code(self) -> list:
#         """Create AST nodes for timing setup"""
#         start_time_code = """
# start_time = time.time()
# """
        
#         progress_start_code = f"""
# yield {{
#     'func': '{self.func_name}',
#     'event': 'started',
#     'time': 0
# }}
# """
#         return [
#             create_ast_from_str(start_time_code),
#             create_ast_from_str(progress_start_code)
#         ]

#     def create_timing_end_code(self, result_var: str) -> list:
#         """Create AST nodes for final timing and progress reporting"""
#         timing_end_code = """
# elapsed_time = time.time() - start_time
# """
        
#         progress_end_code = f"""
# yield {{
#     'func': '{self.func_name}',
#     'event': 'completed',
#     'time': elapsed_time,
#     'result': {result_var}
# }}
# """
        
#         return [
#             create_ast_from_str(timing_end_code),
#             create_ast_from_str(progress_end_code)
#         ]

#     def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
#         """Transform function definitions to include timing and progress reporting"""
#         # Store original function body
#         original_body = node.body
        
#         # Initialize new body with timing setup
#         new_body = self.create_timing_code()
        
#         # Initialize result variable at the start
#         result_var = '_final_result'
#         init_result = f"""
# {result_var} = None
# """
#         new_body.append(create_ast_from_str(init_result))
        
#         # Transform each statement
#         for stmt in original_body[:-1]:  # Process all but the last statement
#             if isinstance(stmt, ast.Return):
#                 if isinstance(stmt.value, ast.Call):
#                     # Handle function call in return
#                     temp_var = self.get_temp_var()
#                     call_stmts = self.transform_call(stmt.value, temp_var)
#                     new_body.extend(call_stmts)
#                     new_body.append(create_ast_from_str(f"{result_var} = {temp_var}"))
#                 else:
#                     # Handle direct return value
#                     new_body.append(create_ast_from_str(f"{result_var} = {ast.unparse(stmt.value)}"))
#             else:
#                 transformed = self.visit(stmt)
#                 if isinstance(transformed, list):
#                     new_body.extend(transformed)
#                 else:
#                     new_body.append(transformed)
        
#         # Handle the last statement separately (typically return)
#         last_stmt = original_body[-1]
#         if isinstance(last_stmt, ast.Return):
#             if isinstance(last_stmt.value, ast.Call):
#                 # Handle function call in return
#                 temp_var = self.get_temp_var()
#                 call_stmts = self.transform_call(last_stmt.value, temp_var)
#                 new_body.extend(call_stmts)
#                 new_body.append(create_ast_from_str(f"{result_var} = {temp_var}"))
#             else:
#                 # Handle direct return value
#                 new_body.append(create_ast_from_str(f"{result_var} = {ast.unparse(last_stmt.value)}"))
#         else:
#             transformed = self.visit(last_stmt)
#             if isinstance(transformed, list):
#                 new_body.extend(transformed)
#             else:
#                 new_body.append(transformed)
        
#         # Add final timing and progress reporting
#         new_body.extend(self.create_timing_end_code(result_var))
        
#         node.body = new_body
#         return node

#     def visit_Assign(self, node: ast.Assign) -> list:
#         if isinstance(node.value, ast.Call):
#             # Handle function calls in assignments
#             temp_var = self.get_temp_var()
#             call_stmts = self.transform_call(node.value, temp_var)
            
#             # Create the final assignment using the temporary variable
#             assign_code = f"""
# {ast.unparse(node.targets[0])} = {temp_var}
# """
#             final_assign = create_ast_from_str(assign_code)
            
#             return call_stmts + [final_assign]
#         return [self.generic_visit(node)]

#     def visit_Return(self, node: ast.Return) -> list:
#         if isinstance(node.value, ast.Call):
#             # Handle function calls in return statements
#             temp_var = self.get_temp_var()
#             call_stmts = self.transform_call(node.value, temp_var)
            
#             # Store result in final result variable
#             result_assign = f"""
# _final_result = {temp_var}
# """
#             return call_stmts + [create_ast_from_str(result_assign)]
#         else:
#             # Handle direct return values
#             result_assign = f"""
# _final_result = {ast.unparse(node.value)}
# """
#             return [create_ast_from_str(result_assign)]

#     def transform_call(self, node: ast.Call, temp_var: str) -> list:
#         """Transform a function call to use yield from if it's a streaming function"""
#         if isinstance(node.func, ast.Name) and node.func.id in self.streaming_funcs:
#             # Create generator from streaming call
#             gen_temp = self.get_temp_var()
            
#             # Build the call arguments string
#             args = [ast.unparse(arg) for arg in node.args]
#             kwargs = [f"{kw.arg}={ast.unparse(kw.value)}" for kw in node.keywords]
#             all_args = ', '.join(args + kwargs)
            
#             # Initialize variable
#             init_code = f"""
# {temp_var} = None
# """
        
#             # Create streaming call
#             stream_code = f"""
# {gen_temp} = {node.func.id}.stream({all_args})
# """
        
#             # Collect all progress events and handle results
#             progress_code = f"""
# for _progress in {gen_temp}:
#     if 'result' in _progress:
#         {temp_var} = _progress['result']
#     yield _progress
# """
        
#             # Verify result
#             verify_code = f"""
# if {temp_var} is None:
#     raise RuntimeError("No result received from {node.func.id}")
# """
        
#             return [
#                 create_ast_from_str(init_code),
#                 create_ast_from_str(stream_code),
#                 create_ast_from_str(progress_code),
#                 create_ast_from_str(verify_code),
#             ]
#         else:
#             # Regular function call
#             call_code = f"""
# {temp_var} = {ast.unparse(node)}
# """
#             return [create_ast_from_str(call_code)]
        
