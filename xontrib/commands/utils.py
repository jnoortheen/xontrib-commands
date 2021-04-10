import builtins
import functools
import typing as tp

from xonsh.built_ins import XonshSession

xsh = tp.cast(XonshSession, builtins.__xonsh__)


class Command:
    def __init__(self, func: tp.Callable, **kwargs):
        """Convert the given function to alias and also create a argparser for its parameters"""
        dashed_name = func.__name__.strip("_").replace("_", "-")
        kwargs["func"] = func
        self.kwargs = kwargs
        self.subs = []
        # convert to
        builtins.aliases[dashed_name] = self.handle_cmd

    @classmethod
    def reg(cls, func, **kwargs):
        """pickle safe way to register alias function"""
        cls(func, **kwargs)
        return func

    @property
    @functools.lru_cache()
    def parser(self):
        import arger
        import argparse

        parser = arger.Arger(
            **self.kwargs, formatter_class=argparse.RawTextHelpFormatter
        )
        for sub in self.subs:
            parser.add_cmd(sub)
        return parser

    def handle_cmd(self, args, stdout):
        self.parser.set_defaults(_stdout=stdout)
        self.parser.run(*args)

    def add(self, func):
        self.subs.append(func)
        return self


def run(*args) -> str:
    """helper function to run shell commands inside xonsh session"""
    import shlex

    cmd_args = list(args)
    if len(args) == 1 and isinstance(args[0], str) and " " in args[0]:
        first_arg = args[0]

        if " | " in first_arg:
            cmds = first_arg.split(" | ")
            cmds = map(lambda x: shlex.split(x), cmds)
            cmd_args = list(cmds)
        else:
            cmd_args = shlex.split(first_arg)
    return xsh.subproc_captured_stdout(cmd_args)
