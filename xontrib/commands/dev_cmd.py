import operator
import os
import typing as tp
from pathlib import Path

import xonsh.tools as xt
from arger import Argument

from .utils import Command, xsh

ENVS = {}


@xt.lazyobject
def added_file_path() -> Path:
    return (
        Path(xsh.env.get("XDG_DATA_HOME", "~/.local/share")).resolve()
        / "dev-paths.json"
    )


def update_saved_paths(paths=()):
    import json

    file = tp.cast(Path, added_file_path)
    if paths:
        content = json.dumps(list(set(paths)))
        file.write_text(content)


def get_added_paths(add_path: str = None) -> tp.Dict[str, str]:
    import json

    file = tp.cast(Path, added_file_path)

    if file.exists():
        paths = json.loads(file.read_text())
    else:
        paths = []
    if add_path:
        paths.append(add_path)
        update_saved_paths(paths)

    return {os.path.split(p)[-1]: p for p in paths}


def register_project(fn: tp.Callable = None):
    """Register new project.

    Parameters
    ----------
    call
        This function will get invoked upon finding the project_path.
        the function name will be used to search in $PROJECT_PATHS
    """

    def _wrapper():
        path = _start_proj_shell(fn.__name__)
        result = fn(path)

        return result

    ENVS[fn.__name__] = _wrapper
    return _wrapper


def _start_proj_shell(env: tp.Union[str, Path]):
    if isinstance(env, Path) and env.exists():
        path = str(env)
    else:
        path = find_proj_path(env)
        if not path:
            raise Exception("Project not found")
    os.chdir(path)
    return path


def _find_proj_path(name, op):
    for direc in xsh.env.get("PROJECT_PATHS", []):
        for path in Path(direc).glob("*"):
            if op(path.name, name):
                return path


def find_proj_path(name):
    for op in [operator.eq, str.startswith, operator.contains]:
        path = _find_proj_path(name, op)
        if path:
            return path


def _list_cmds():
    from rich.console import Console

    c = Console()
    paths = get_added_paths()
    c.print("Paths", paths)


def _add_current_path():
    from rich.console import Console

    c = Console()
    path = Path.cwd().resolve()
    c.log("Adding cwd to project-paths", {path.name: path})
    get_added_paths(str(path))


@Command.reg
def _dev(
    _arger_,
    _namespace_,
    name: tp.cast(str, Argument(nargs="?")),
    add=False,
    ls=False,
):
    """A command to cd into a directory

    Inspired from my own workflow and these commands
        - https://github.com/ohmyzsh/ohmyzsh/tree/master/plugins/pj
        - https://github.com/ohmyzsh/ohmyzsh/tree/master/plugins/wd

    Parameters
    ----------
    name
        name of the folder to cd into.
        This searches for names under $PROJECT_PATHS
        or the ones registered with `dev --add`
    add
        register the current folder to dev command.
        When using this, it will get saved in a file,
        also that is used during completions.
    ls
        show currently registered paths

    Notes
    -----
        One can use `register_project` function to regiter custom_callbacks to run on cd to project path

    Examples
    -------
        > $PROJECT_PATHS = ["~/src/"]
        > dev proj-name # --> will cd into ~/src/proj-name
        > dev --add
    """

    if ls:
        _list_cmds()
    elif add:
        _add_current_path()
    else:
        added_paths = get_added_paths()
        if name in ENVS:
            ENVS[name]()
        elif name in added_paths:
            path = added_paths[name]
            if os.path.exists(path):
                return _start_proj_shell(Path(path))
            else:
                # old/expired link
                added_paths.pop(name)
                update_saved_paths(tuple(added_paths.values()))

        return _start_proj_shell(name)
