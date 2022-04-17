import re
from functools import cached_property
from typing import Any, Callable, List, Optional

import arger

from xonsh.built_ins import XSH
from xonsh.cli_utils import get_argparse_formatter_class, ArgParserAlias
from xonsh.completers.tools import RichCompletion
from xonsh.parsers.completion_context import CommandContext

xsh = XSH


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
        xsh.aliases[self.prog] = self

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


def run(*args, capture: Optional[bool] = None) -> str:
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
    # from xonsh.built_ins import (
    #     subproc_captured_stdout as capt,
    #     subproc_uncaptured as run,
    # )
    #
    # HAVE_UGLIFY = bool(capt(["which", "uglifyjs"]))
    # run(
    #     ["uglifyjs", js_target, "--compress", UGLIFY_FLAGS],
    #     "|",
    #     ["uglifyjs", "--mangle", "--output", min_target],
    # )
    return func(cmd_args)


class NuclearCompleter:
    builder: Any

    @cached_property
    def hyphen_param_matcher(self):
        return re.compile(r"-(.+)=(.+)")

    def generate_value_choices(self, rule, **kwargs):
        if not rule.choices:
            return

        if callable(rule.choices):
            yield from rule.choices(rule=rule, **kwargs)
            return

        # sequence
        yield from rule.choices

    def iter_completions(self, rule):
        for kw in rule.keywords:
            yield RichCompletion(kw, description=rule.help)

    def _find_available_completions(self, rules, args, current_word, **extra):
        """updated from nuclear"""
        from nuclear.builder.rule import (
            FlagRule,
            ParameterRule,
            PrimaryOptionRule,
            PositionalArgumentRule,
            ManyArgumentsRule,
            SubcommandRule,
            CliRule,
        )
        from nuclear.parser.transform import filter_rules
        from nuclear.parser.parser import Parser
        from nuclear.parser.context import RunContext

        subcommands: List[SubcommandRule] = filter_rules(rules, SubcommandRule)
        run_context: Optional[RunContext] = Parser(rules, dry=True).parse_args(args)
        all_rules: List[CliRule] = run_context.active_rules
        active_subcommands: List[SubcommandRule] = run_context.active_subcommands
        if active_subcommands:
            subcommands = filter_rules(active_subcommands[-1].subrules, SubcommandRule)

            # current word is exactly the last command
            if current_word in active_subcommands[-1].keywords:
                yield current_word
                return

        flags = filter_rules(all_rules, FlagRule)
        parameters = filter_rules(all_rules, ParameterRule)
        primary_options = filter_rules(all_rules, PrimaryOptionRule)
        pos_arguments = filter_rules(all_rules, PositionalArgumentRule)
        many_args = filter_rules(all_rules, ManyArgumentsRule)

        # "--param value" autocompletion
        previous: Optional[str] = args[-2] if len(args) > 1 else None
        if previous:
            for rule in parameters:
                for keyword in rule.keywords:
                    if previous == keyword:
                        yield from self.generate_value_choices(
                            rule, current=current_word, **extra
                        )
                        return

        # "--param=value" autocompletion
        for rule in parameters:
            for keyword in rule.keywords:
                if current_word.startswith(keyword + "="):
                    yield from map(
                        lambda c: keyword + "=" + c,
                        self.generate_value_choices(
                            rule, current=current_word, **extra
                        ),
                    )
                    return

        for cont in [subcommands, flags, parameters, primary_options]:
            for rule in cont:
                yield from self.iter_completions(rule)
        for cont in [pos_arguments, many_args]:
            for rule in cont:
                yield from self.generate_value_choices(
                    rule, current=current_word, **extra
                )

    def xonsh_complete(self, command: CommandContext, **kwargs):
        from nuclear.autocomplete.autocomplete import get_current_word

        all_args = [a.raw_value for a in command.args]
        args = all_args[1:]  # exclude first arg
        current_word = get_current_word(args, command.arg_index)
        comps = self._find_available_completions(
            self.builder._CliBuilder__subrules,
            args,
            current_word,
            command=command,
            **kwargs
        )
        # yield from comps
        for c in comps:
            if c.startswith(current_word):
                yield c
                # yield escape_spaces(self.hyphen_param_matcher.sub("\\2", c))
