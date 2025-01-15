"""
Decorator module
"""

from argparse import ArgumentParser
from typing import Callable, List, Optional, Tuple, Union


def argument(*name_of_flags, **kwargs):
    """
    Argparse argument function
    """
    return (list(name_of_flags), kwargs)


def command(
    args: Optional[Union[Union[str, Callable], list]] = None,
    parent: Optional[ArgumentParser] = None,
    aliases: Optional[List[str]] = None,
) -> Callable:
    """
    Decorator for argument parser
    :param ArgumentParser parent: parent for arguments
    :param list[argument] args: unknow
    :param list[str] cmd_aliases: aliases for cli option
    """
    if aliases is None:
        aliases = []
    if args is None:
        args = []

    def decorator(func):
        parser = parent.add_parser(
            func.__name__.replace("_", "-"),
            description=func.__doc__,
            aliases=aliases,
        )
        for arg in args:
            parser.add_argument(*arg[0], **arg[1])
        parser.set_defaults(func=func)

    return decorator
