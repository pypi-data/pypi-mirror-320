from functools import wraps
from typing import Any, Callable, Generator

def get_stream_function(func: Callable) -> Callable:
    """
    Creates a streaming version of a function that yields execution states.
    
    Args:
        func (Callable): The function to be wrapped
        
    Returns:
        Callable: A wrapped function that yields 'started' and ('done', result)
        
    Example:
        def add(a, b):
            return a + b
            
        stream_add = get_stream_function(add)
        generator = stream_add(1, 2)
        assert next(generator) == 'started'
        assert next(generator) == ('done', 3)
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Generator[Any, None, None]:
        # Yield 'started' state
        yield 'started'
        
        # Execute the function and store result
        result = func(*args, **kwargs)
        
        # Yield 'done' state with the result
        yield ('done', result)
        
    return wrapper