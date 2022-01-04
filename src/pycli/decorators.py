"""Define the cli decorator that is used to ease use of the CliParser."""
from functools import wraps
from typing import Any, Callable

from pycli.parser import CliParser, Cls


def cli(clz: Cls, *, constructor: str = "__init__", **kwargs):
    """Decorate a method to turn it into a CLI entry-point.

    After a method is decorated, the method's first positional
    argument should be for a class instance which will be loaded
    using the CLI arguments.

    Parameters
    ----------
    clz : Cls
        The class to bind to the argument parser.
    constructor : str
        The class constructor to use. This defaults to __init__.
    **kwargs
        Additional keyword arguments to pass to the parser
        (which will ultimately be passed to ArgumentParser).

    Example
    -------

    >>> class MyClass:
    ...     a: int
    ...     b: str
    ...
    >>> @cli(MyClass)
    ... def cli_entry_point(obj: MyClass):
    ...     print(obj)
    ...
    >>> cli_entry_point()
    """

    def inner(func) -> Callable[[Any], Callable[[Any], Cls]]:
        @wraps(func)
        def inner_wrapper(*sys_args, **sys_kwargs) -> Cls:
            argv = None
            if sys_args:
                argv = sys_args[0]
            elif sys_kwargs:
                argv = sys_kwargs.get("args", None)

            parser = CliParser(clz=clz, constructor=constructor, **kwargs)
            args = parser.parse_args(argv)
            return func(args)

        return inner_wrapper

    return inner
