import builtins
import inspect
import typing as tp
from collections import defaultdict

from .utils import Command


def format_key(k) -> str:
    if hasattr(k, "value"):
        return k.value.replace("c-", "Ctrl-").replace("s-", "Shift-")
    return str(k)


def _get_keybindgs():
    from prompt_toolkit.key_binding.key_bindings import Binding

    bindings: tp.List[Binding] = builtins.__xonsh__.shell.prompter.key_bindings.bindings

    keys = defaultdict(list)
    for i in bindings:

        key_formatted = " + ".join([format_key(k) for k in i.keys])
        if key_formatted.startswith("Keys"):
            key_formatted = key_formatted.replace("Keys.", "")
        keys[i.handler].append(key_formatted)

    return keys


def _grouped_by_modules():
    bindings = _get_keybindgs()
    mod_keys = defaultdict(list)
    for handle, keys in bindings.items():
        mod_keys[handle.__module__].append((handle, keys))

    handle_counter = defaultdict(int)
    single_counter = []
    for mod, handles in mod_keys.items():
        count = len(handles)
        if count > 1:
            handle_counter[mod] = len(handles)
        else:
            single_counter.append(mod)

    final_cont = defaultdict(list)
    for mod in sorted(handle_counter):
        final_cont[mod] = mod_keys[mod]

    for mod in single_counter:
        final_cont["..."].extend(mod_keys[mod])

    return final_cont


@Command.reg
def report_key_bindings(_stdout):
    """Show current Prompt-toolkit bindings in a nice table format"""

    from rich.console import Console
    from rich.table import Table

    mod_keys = _grouped_by_modules()
    tables = []
    for mod, handles in mod_keys.items():
        mod_table = Table(
            pad_edge=False,
            # box=None,
            expand=True,
            show_lines=True,
            title=f"[green]{mod}[/green]",
        )
        mod_table.add_column("Keys", style="dim")
        mod_table.add_column("Description")
        for handle, keys in handles:
            module = f"{handle.__module__ if mod == '...' else ''}.{handle.__name__}"
            docstr = inspect.getdoc(handle) or ""
            mod_table.add_row(
                "\n".join(keys), ". ".join([docstr, f"[blue]fn: {module}[/blue]"])
            )
        tables.append(mod_table)

    console = Console()
    # https://bugs.python.org/issue37871
    # with console.pager():
    console.print(*tables)


def term_test(c):
    from rich import inspect

    inspect(c)
