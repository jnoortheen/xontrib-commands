"""Command to get current key-bidings in table-format"""
import builtins
import inspect
import sys
import typing as tp
from collections import defaultdict

import functools


class Command:
    def __init__(self, func: tp.Callable, **kwargs):
        """Convert the given function to alias and also create a argparser for its parameters"""
        dashed_name = func.__name__.replace('_', '-')
        kwargs["func"] = func
        self.kwargs = kwargs
        # convert to
        builtins.aliases[dashed_name] = self.handle_cmd

    @property
    @functools.lru_cache()
    def parser(self):
        import arger
        import argparse

        return arger.Arger(**self.kwargs, formatter_class=argparse.RawTextHelpFormatter)

    def handle_cmd(self, args):
        self.parser.run(*args)


def _get_keybindgs():
    from prompt_toolkit.key_binding.key_bindings import Binding
    bindings: tp.List[Binding] = builtins.__xonsh__.shell.prompter.key_bindings.bindings

    keys = defaultdict(list)
    for i in bindings:
        keys[i.handler].extend([k.value if hasattr(k, "value") else str(k) for k in i.keys])

    return keys


@Command
def report_key_bindings():
    """Show current Prompt-toolkit bindings in a nice table format
    """
    from rich.console import Console
    from rich.table import Table
    bindings = _get_keybindgs()
    tbl = Table(show_lines=True)
    tbl.add_column("Keys", style="dim")
    tbl.add_column("Description")
    tbl.add_column("Module")

    for handle, keys in bindings.items():
        module = f"{handle.__module__}.{handle.__name__}"

        docstr = inspect.getdoc(handle)
        tbl.add_row(
            "\n".join(keys),
            docstr or module,
            module
        )

    c = Console()
    with c.pager():
        c.print(tbl)


@Command
def reload_mods(name: str):
    """Reload any python module in the current xonsh session.
    Helpful during development.

    Parameters
    ----------
    name:
        Name of the module/package to reload.
        Giving partial names matches all the nested modules.

    Examples
    -------
    $ reload-mods xontrib
        - this will reload all modules imported that starts with xontrib name

    Notes
    -----
        Please use
            `import module` or `import module as mdl` patterns
        Using
            `from module import name`
            will not reload the name imported
    """
    # todo: implement a watcher mode
    import importlib

    modules = list(sys.modules)  # create a copy of names. so that it will not raise warning
    for mod_name in modules:
        mod = sys.modules[mod_name]
        if name and not mod_name.startswith(name):
            continue
        print("reload ", mod_name)
        try:
            importlib.reload(mod)
        except Exception as e:
            print("failed to reload", mod_name, e)
