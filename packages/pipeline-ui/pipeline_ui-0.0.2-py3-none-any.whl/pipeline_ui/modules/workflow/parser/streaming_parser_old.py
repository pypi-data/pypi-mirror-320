# import ast
# import inspect
# from typing import Callable


# def transform_to_generator(func: Callable) -> Callable:
#     """
#     Transform a regular function into a generator function that yields intermediate outputs.

#     This function takes a callable as input and returns a new function that behaves like
#     a generator. The transformed function will yield dictionaries containing intermediate
#     outputs after each assignment and before the return statement.

#     The transformation process:
#     1. Parses the input function's source code into an Abstract Syntax Tree (AST).
#     2. Modifies the AST to include yield statements after assignments and before returns.
#     3. Compiles the modified AST back into a Python function.
#     4. Executes the new function in a namespace that includes the original function's globals.

#     Args:
#         func (Callable): The input function to be transformed.

#     Returns:
#         Callable: A new function that behaves like a generator, yielding intermediate outputs.

#     Yields:
#         dict: Dictionaries containing either 'output' key for intermediate results,
#               or 'end' key for the final return value.

#     Example:
#         >>> def get_number_twice(x: int) -> tuple[int, int]:
#         ...     return x, x
#         >>>
#         >>> def add_numbers(a: int, b: int) -> int:
#         ...     return a + b
#         >>>
#         >>> def example_workflow_simple(x: int, y: int) -> int:
#         ...     a, b = get_number_twice(x)
#         ...     c = add_numbers(a, b)
#         ...     return c
#         >>>
#         >>> transformed_workflow = transform_to_generator(example_workflow_simple)
#         >>>
#         >>> for step in transformed_workflow(5, 3):
#         ...     print(step)
#         {'output': (5, 5)}
#         {'output': 10}
#         {'end': 10}
#     """

#     source = inspect.getsource(func)
#     parsed = ast.parse(source)

#     # Find the function definition
#     func_def = None
#     for node in parsed.body:
#         if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == func.__name__:
#             func_def = node
#             break

#     if func_def is None:
#         raise ValueError("Function definition not found")

#     class TransformToGenerator(ast.NodeTransformer):
#         def visit_FunctionDef(self, node):
#             # Modify the function to be a generator function
#             node.decorator_list = []
#             # Remove the return type annotation if any
#             node.returns = None
#             # Process the body
#             self.generic_visit(node)
#             return node

#         def visit_Assign(self, node):
#             # Visit the node to process any child nodes
#             new_node = self.generic_visit(node)
#             # Get an expression that evaluates to the assigned variables
#             assigned_expr = self.targets_to_expr(node.targets)
#             # Create the yield expression
#             yield_expr = ast.Expr(
#                 value=ast.Yield(value=ast.Dict(keys=[ast.Constant(value="output")], values=[assigned_expr]))
#             )
#             return [new_node, yield_expr]

#         def visit_Return(self, node):
#             # Visit the node to process any child nodes
#             return_value = self.visit(node.value)
#             # Create the yield expression
#             yield_expr = ast.Expr(
#                 value=ast.Yield(value=ast.Dict(keys=[ast.Constant(value="end")], values=[return_value]))
#             )
#             # Remove the return statement
#             return [yield_expr]

#         def targets_to_expr(self, targets):
#             if len(targets) == 1:
#                 target = targets[0]
#                 return self.change_context(target, ast.Load())
#             else:
#                 # Multiple targets, we can create a tuple of the targets
#                 elts = [self.change_context(target, ast.Load()) for target in targets]
#                 return ast.Tuple(elts=elts, ctx=ast.Load())

#         def change_context(self, node, ctx):
#             if isinstance(node, ast.Name):
#                 return ast.Name(id=node.id, ctx=ctx)
#             elif isinstance(node, ast.Tuple):
#                 return ast.Tuple(elts=[self.change_context(elt, ctx) for elt in node.elts], ctx=ctx)
#             elif isinstance(node, ast.Subscript):
#                 return ast.Subscript(
#                     value=self.change_context(node.value, ctx),
#                     slice=node.slice,
#                     ctx=ctx,
#                 )
#             elif isinstance(node, ast.Attribute):
#                 return ast.Attribute(value=self.change_context(node.value, ctx), attr=node.attr, ctx=ctx)
#             else:
#                 return node

#     # Modify the AST
#     transformer = TransformToGenerator()
#     transformer.visit(func_def)
#     ast.fix_missing_locations(parsed)

#     # Compile the modified AST
#     code = compile(parsed, filename="<ast>", mode="exec")

#     # Create a namespace to execute the code
#     namespace = {}
#     # Include the globals from the original function
#     namespace.update(func.__globals__)
#     # Execute the compiled code
#     exec(code, namespace)
#     # Get the transformed function
#     transformed_func = namespace[func.__name__]

#     return transformed_func



# test = {
#     "invokation_order": ['func1', 'func2', 'func3'],
# }

# test = {
#     "type": "workflow",
#     "status": "invoked",
#     "name": "workflow_name",
# }

# test = {
#     "type": "node",
#     "status": "invoked",
#     "name": "function_name",
#     "args": [1, 2, 3],
#     "kwargs": {"a": 1, "b": 2},
# }

# test = {
#     "type": "node",
#     "status": "done",
#     "name": "function_name",
#     "output": 10,
# }

# test = {
#     "type": "node",
#     "status": "error",
#     "name": "function_name",
#     "error": "An error occurred",
# }


# test = {
#     "type": "workflow",
#     "status": "done",
#     "name": "workflow_name",
#     "output": 10,
# }

