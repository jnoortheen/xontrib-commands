import sys

from arger import Argument
from typing_extensions import Annotated

from .utils import Command


def module_name_completer(**_):
    yield from sys.modules


@Command.reg
def reload_mods(name: Annotated[str, Argument(completer=module_name_completer)]):
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
    from rich.console import Console

    console = Console()
    modules = list(
        sys.modules
    )  # create a copy of names. so that it will not raise warning
    for mod_name in modules:
        mod = sys.modules[mod_name]
        if name and not mod_name.startswith(name):
            continue
        console.print(f"reload [cyan] {mod_name}[/cyan]")
        try:
            importlib.reload(mod)
        except Exception as e:
            console.print("[red]failed to reload [/red]", mod_name, e)
