# from functools import wraps




# def get_stream_function(func: Callable) -> Callable:
#     """
#     Creates a streaming version of a function that yields execution states,
#     including states from nested function calls. Can be run normally by passing
#     stream=False.
    
#     Args:
#         func (Callable): The function to be wrapped
        
#     Returns:
#         Callable: A wrapped function that either yields states or runs normally
        
#     Example:
#         @get_stream_function
#         def add(a, b):
#             return a + b
            
#         # Streaming mode
#         generator = add(1, 2, stream=True)
#         for state in generator:
#             print(state)
            
#         # Normal mode
#         result = add(1, 2, stream=False)  # or just add(1, 2)
#         print(result)
#     """
#     @wraps(func)
#     def wrapper(*args, **kwargs) -> Union[Generator[Dict[str, Any], None, None], Any]:
#         # Extract stream parameter, defaulting to True for backward compatibility
#         stream = kwargs.pop('stream', True)
        
#         # If streaming is disabled, run the function normally
#         if not stream:
#             return func(*args, **kwargs)
            
#         # Get the current nesting level from kwargs or default to 0
#         current_level = kwargs.pop('_stream_level', 0)
        
#         # Yield 'started' state with nesting level
#         yield {
#             'event': 'started',
#             'func': func.__name__,
#             'level': current_level
#         }
        
#         try:
#             # Execute the function and store result
#             result = func(*args, **kwargs)
            
#             # If result is a generator (from another wrapped function),
#             # yield all its states with increased nesting level
#             if isinstance(result, Generator):
#                 try:
#                     while True:
#                         inner_state = next(result)
#                         if isinstance(inner_state, dict) and 'event' in inner_state:
#                             inner_state['level'] = current_level + 1
#                             yield inner_state
#                 except StopIteration as e:
#                     result = e.value
            
#             # Yield 'done' state with the result
#             yield {
#                 'event': 'done',
#                 'func': func.__name__,
#                 'level': current_level,
#                 'output': str(result) if result is not None else None
#             }
            
#             return result
            
#         except Exception as e:
#             # Yield error state if an exception occurs
#             yield {
#                 'event': 'error',
#                 'func': func.__name__,
#                 'level': current_level,
#                 'error': str(e)
#             }
#             raise
    
#     return wrapper

# def node_decorator(func, pui: PipelineUI):
#     pui.add_node(func)

#     stream_func = get_stream_function(func)
    
#     @wraps(func)
#     def wrapper(*args, **kwargs):
#         # If streaming is disabled for this node, run normally
#         stream = kwargs.pop('stream', False)

#         if not stream:
#             return func(*args, **kwargs)
        
#         generator = stream_func(*args, **kwargs)
#         try:
#             for state in generator:
#                 # Handle the state here - you can emit it to your UI
#                 print(f"Node {state['func']} - {state['event']} (level {state['level']})")
#                 if state['event'] == 'done':
#                     if state.get('output') is not None:
#                         return state.get('output')
#                 elif state['event'] == 'error':
#                     raise Exception(state['error'])
#         except StopIteration as e:
#             return e.value
    
#     return wrapper