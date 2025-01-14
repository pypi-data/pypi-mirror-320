"""Define functions to secure the parameters of functions.

Functions
---------
* freezeparams(func) - Secure mutable parameters from modifications.
"""

import copy
import inspect
import functools
from typing import Any, Callable


def freezeparams(func: Callable[..., Any]) -> Callable[..., Any]:
    """Secure mutable parameters from modifications.

    At each call of the decorated function `func`, it ensures the integrity
    of parameters with mutable default values and parameters receiving mutable
    arguments, preventing any accidental modifications and isolating the calls
    ,making the code more reliable and predictable.

    Parameters
    ----------
    func: Callable[..., Any]
        The function to decorate.

    Returns
    -------
    Callable[..., Any]
        A new function with secure mutable parameters.

    Example
    -------
    >>> @freezeparams
    ... def add_to(value, liste=[]):
    ...    liste.append(value)
    ...    return liste
    ...
    >>> add_to(56)
    [56]
    >>> add_to(value=98)
    [98]
    >>> my_list = [1, 2]
    >>> add_to(3, my_list)
    [1, 2, 3]
    >>> my_list
    [1, 2]
    >>>
    """

    @functools.wraps(func)
    def wrapper(*args: tuple[Any], **kwargs: dict[str, Any]) -> Any:
        parameters = inspect.signature(func).parameters
        default_kwargs = {
            key: value
            for key, param in parameters.items()
            if (value := param.default) != inspect.Parameter.empty
        }

        args_to_kwargs: dict[str, Any] = {}
        if args:
            args = copy.deepcopy(args)
            bound_arguments = inspect.signature(func).bind(*args)
            bound_arguments.apply_defaults()
            args_to_kwargs = bound_arguments.arguments
            args = ()

        kwargs = copy.deepcopy(default_kwargs | args_to_kwargs | kwargs)

        return func(*args, **kwargs)

    return wrapper
