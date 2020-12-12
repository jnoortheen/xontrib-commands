import operator
import os
import typing as tp

from .utils import Command, xsh
import xonsh.tools as xt
from pathlib import Path

ENVS = {}


@xt.lazyobject
def added_file_path() -> Path:
    return (
        Path(xsh.env.get("XDG_DATA_HOME", "~/.local/share")).resolve()
        / "dev-paths.json"
    )


def get_added_paths(add_path: str = None) -> tp.Dict[str, str]:
    import json

    file = tp.cast(Path, added_file_path)

    if file.exists():
        paths = json.loads(file.read_text())
    else:
        paths = []
    if add_path:
        paths.append(add_path)
        content = json.dumps(list(set(paths)))
        file.write_text(content)
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
    for direc in xsh.env.get("PROJECT_PATH", []):
        for path in Path(direc).glob("*"):
            if op(path.name, name):
                return path


def find_proj_path(name):
    for op in [operator.eq, str.startswith, operator.contains]:
        path = _find_proj_path(name, op)
        if path:
            return path


@Command
def _dev(_arger_, _namespace_, name: str):
    """A command to cd into a directory

    Inspired from my own workflow and these commands
        - https://github.com/ohmyzsh/ohmyzsh/tree/master/plugins/pj
        - https://github.com/ohmyzsh/ohmyzsh/tree/master/plugins/wd

    Parameters
    ----------
    name
        - name of the folder to cd into.
            This searches for names under $PROJECT_PATHS
            or the ones registered with `dev --add`
    Notes
    -----
        One can use `register_project` function to regiter custom_callbacks to run on cd to project path

    Examples
    -------
        > $PROJECT_PATHS = ["~/src/"]
        > dev proj-name # --> will cd into ~/src/proj-name
    """
    raise Exception
    added_paths = get_added_paths()
    if name in ENVS:
        ENVS[name]()
    elif name in added_paths:
        return _start_proj_shell(Path(added_paths[name]))
    else:
        return _start_proj_shell(name)


@Command
def _dev_add(ls=False):
    """register the current folder to dev command.
    When using this, it will get saved a file,
    also that is used during completions, and fuzzy search on them will work.

    Parameters
    ----------
    ls
        show currently registered paths
    """
    from rich.console import Console

    c = Console()

    if ls:
        paths = get_added_paths()
        c.print("Paths", paths)
    else:
        path = Path.cwd().resolve()
        c.log("Adding cwd to project-paths", {path.name: path})
        get_added_paths(str(path))
