import arger
from typing import Callable

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

    def __init__(self, func: Callable, threadable=True, capturable=True, **kwargs):
        """Convert the given function to alias and also create a argparser for its parameters"""
        super().__init__()
        self.prog = func.__name__.strip("_").replace("_", "-")
        if not threadable:
            from xonsh.tools import unthreadable

            unthreadable(self)
        if not capturable:
            from xonsh.tools import uncapturable

            uncapturable(self)

        kwargs["func"] = func
        kwargs["prog"] = self.prog
        self.kwargs = kwargs

        # convert to
        XSH.aliases[self.prog] = self

    @classmethod
    def reg(cls, func, **kwargs):
        """pickle safe way to register alias function"""
        cls(func, **kwargs)
        return func

    @classmethod
    def reg_no_thread(cls, func, **kwargs):
        """pickle safe way to register alias function that is not threadable"""
        kwargs.setdefault("threadable", False)
        return cls.reg(func, **kwargs)

    @classmethod
    def reg_no_cap(cls, func, **kwargs):
        """pickle safe way to register alias function that is not capturable"""
        kwargs.setdefault("capturable", False)
        return cls.reg(func, **kwargs)

    def build(self) -> "Arger":
        return Arger(**self.kwargs)

    def __call__(
        self, args, stdin=None, stdout=None, stderr=None, spec=None, stack=None
    ):
        self.parser.set_defaults(_stdin=stdin)
        self.parser.set_defaults(_stdout=stdout)
        self.parser.set_defaults(_stderr=stderr)
        self.parser.set_defaults(_spec=spec)
        self.parser.set_defaults(_stack=stack)
        self.parser.run(*args, capture_sys=False)
