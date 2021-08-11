import typing as tp

import arger

from xonsh.built_ins import XSH
from xonsh.cli_utils import get_argparse_formatter_class, ArgParserAlias

xsh = XSH


class Arger(arger.Arger):
    def add_argument(self, *args, **kwargs):
        completer = kwargs.pop("completer", None)
        action = super().add_argument(*args, **kwargs)
        if completer:
            action.completer = completer
        return action


class Command(ArgParserAlias):
    def __init__(self, func: tp.Callable, **kwargs):
        """Convert the given function to alias and also create a argparser for its parameters"""
        super().__init__()
        dashed_name = func.__name__.strip("_").replace("_", "-")
        kwargs["func"] = func
        self.kwargs = kwargs
        # convert to
        xsh.aliases[dashed_name] = self

    @classmethod
    def reg(cls, func, **kwargs):
        """pickle safe way to register alias function"""
        cls(func, **kwargs)
        return func

    def build(self) -> "Arger":
        return Arger(**self.kwargs, formatter_class=get_argparse_formatter_class())

    def __call__(
        self, args, stdin=None, stdout=None, stderr=None, spec=None, stack=None
    ):
        self.parser.set_defaults(_stdin=stdin)
        self.parser.set_defaults(_stdout=stdout)
        self.parser.set_defaults(_stderr=stderr)
        self.parser.set_defaults(_spec=spec)
        self.parser.set_defaults(_stack=stack)
        self.parser.run(*args)


def _get_proc_func_():
    import inspect, opcode

    frame = inspect.currentframe()

    try:
        frame = frame.f_back
        next_opcode = opcode.opname[ord(str(frame.f_code.co_code[frame.f_lasti + 3]))]
        if next_opcode == "POP_TOP":
            # or next_opcode == "RETURN_VALUE":
            # include the above line in the if statement if you consider "return run()" to be assignment

            # "I was not assigned"
            return XSH.subproc_uncaptured
    finally:
        del frame
    return XSH.subproc_captured_stdout


def run(*args, capture: tp.Optional[bool] = None) -> str:
    """helper function to run shell commands inside xonsh session"""
    import shlex

    if capture is None:
        func = _get_proc_func_()
    elif capture:
        func = XSH.subproc_captured_stdout
    else:
        func = XSH.subproc_uncaptured

    cmd_args = list(args)
    if len(args) == 1 and isinstance(args[0], str) and " " in args[0]:
        first_arg = args[0]

        if " | " in first_arg:
            cmds = first_arg.split(" | ")
            cmds = map(lambda x: shlex.split(x), cmds)
            cmd_args = list(cmds)
        else:
            cmd_args = shlex.split(first_arg)
    return func(cmd_args)
