from dataclasses import dataclass
from typing import Any, Callable, List, Optional
import inspect

@dataclass
class ArgumentInfo:
    name: str
    type: str
    default: Optional[Any] = None


def get_method_args(method: Callable) -> List[ArgumentInfo]:
    # Get the signature of the method
    signature = inspect.signature(method)
    
    # Get the parameters
    params = signature.parameters
    
    # Convert to list of argument info
    args_info = [
        ArgumentInfo(
            name=name,
            type=str(param.annotation),
            default=param.default if param.default != inspect.Parameter.empty else None,
        )
        for name, param in params.items()
    ]
    
    return args_info