from typing import Callable

import arger

from xonsh.built_ins import XSH
from xonsh.cli_utils import get_argparse_formatter_class, ArgParserAlias


class Arger(arger.Arger):
    def __init__(self, **kwargs):
        kwargs.setdefault("formatter_class", get_argparse_formatter_class())
        super().__init__(**kwargs)

    def add_argument(self, *args, **kwargs):
        completer = kwargs.pop("completer", None)
        action = super().add_argument(*args, **kwargs)
        if completer:
            action.completer = completer
        return action


class Command(ArgParserAlias):
    """Use arger to create commands from functions"""

    def __init__(
        self, func: Callable | Arger, threadable=True, capturable=True, **kwargs
    ):
        """Convert the given function to alias and also create a argparser for its parameters"""
        super().__init__()

        def get_prog_name(func):
            return func.__name__.strip("_").replace("_", "-")

        if isinstance(func, Arger):
            if func.func is not None:
                prog = get_prog_name(func.func)
            else:
                prog = func.prog
            self.arger = func
            self.kwargs = None
        else:
            prog = get_prog_name(func)
            kwargs["func"] = func
            kwargs["prog"] = prog
            self.kwargs = kwargs
            self.arger = None

        if not threadable:
            from xonsh.tools import unthreadable

            unthreadable(self)
        if not capturable:
            from xonsh.tools import uncapturable

            uncapturable(self)

        # convert to
        XSH.aliases[prog] = self

    @classmethod
    def reg(cls, func: Callable | Arger, **kwargs):
        """pickle safe way to register alias function"""
        cls(func, **kwargs)
        return func

    @classmethod
    def reg_no_thread(cls, func: Callable | Arger, **kwargs):
        """pickle safe way to register alias function that is not threadable"""
        kwargs.setdefault("threadable", False)
        return cls.reg(func, **kwargs)

    @classmethod
    def reg_no_cap(cls, func: Callable | Arger, **kwargs):
        """pickle safe way to register alias function that is not capturable"""
        kwargs.setdefault("capturable", False)
        return cls.reg(func, **kwargs)

    def build(self) -> "Arger":
        # override to return build parser
        return Arger(**self.kwargs) if self.arger is None else self.arger

    def __call__(
        self, args, stdin=None, stdout=None, stderr=None, spec=None, stack=None
    ):
        self.parser.set_defaults(_stdin=stdin)
        self.parser.set_defaults(_stdout=stdout)
        self.parser.set_defaults(_stderr=stderr)
        self.parser.set_defaults(_spec=spec)
        self.parser.set_defaults(_stack=stack)
        self.parser.run(*args, capture_sys=False)
