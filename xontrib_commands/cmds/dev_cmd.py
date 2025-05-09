import operator
import os
import typing as tp
from arger import Argument
from pathlib import Path

from xonsh.completers.tools import RichCompletion
from xonsh.parsers.completion_context import CommandContext
from xonsh.built_ins import XSH as xsh

ENVS = {}


class DevPaths:
    def __init__(self):
        self.file = (
        Path(xsh.env.get("XDG_DATA_HOME", "~/.local/share")).resolve()
        / "dev-paths.json"
    )

    def update_saved(self, *paths: str) -> None:
        import json

        if paths:
            content = json.dumps(list(set(paths)))
            self.file.write_text(content)

    def load(self) -> list[str]:
        import json

        if self.file.exists():
            return json.loads(self.file.read_text()) or []
        return []

    def get_added_paths(self, add_path: str | None = None) -> tp.Dict[str, str]:
        paths = self.load()
        if add_path:
            paths.append(add_path)
            self.update_saved(*paths)

        return {os.path.split(p)[-1]: p for p in paths}

    def clean_paths(self):
        from rich.console import Console

        c = Console()
        paths = []
        for path in self.load():
            p = Path(path)
            if not p.exists():
                c.log("Removing paths that no longer exists", {p.name: p})
            else:
                paths.append(path)
        self.update_saved(*paths)


dev_paths = DevPaths()

def register_project(fn: tp.Callable = None):
    """Register new project.

    Parameters
    ----------
    fn
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


def get_uniq_project_paths(*paths):
    """
    >>> get_uniq_project_paths('~/src/py/', '~/src/py/_repos/', '~/src')
    {'~/src'}
    """
    proj_roots: "set[str]" = set(paths)
    for path in list(proj_roots):
        rest = proj_roots.difference({path})
        if path.startswith(tuple(rest)):
            proj_roots.remove(path)
    return proj_roots


def _find_proj_path(name, *funcs):
    paths = xsh.env.get("PROJECT_PATHS", [])
    # todo: use cd from history
    #  1. check history item size. changin it to namedtuple might save some space
    # get_uniq_project_paths() - not using recurse directories, since it is slow
    found_paths = []
    for direc in set(paths):
        root = Path(direc).expanduser()
        if not root.is_dir():
            continue
        for path in root.iterdir():
            if not path.is_dir():
                continue
            for i, op in enumerate(funcs):
                if op(path.name, name):
                    found_paths.append((i, path))
                    
    yield from map(operator.itemgetter(1),sorted(found_paths,key=operator.itemgetter(0)))


def find_proj_path(name):
    """return first found path"""
    for path in _find_proj_path(name, operator.eq, str.startswith, operator.contains):
        return path


def _list_cmds():
    from rich.console import Console

    c = Console()
    paths = dev_paths.get_added_paths()
    c.print("Paths:", paths)


def _add_current_path():
    from rich.console import Console

    c = Console()
    path = Path.cwd().resolve()
    c.log("Adding cwd to project-paths", {path.name: path})
    dev_paths.get_added_paths(str(path))


def proj_name_completer(**kwargs):
    command: CommandContext = kwargs.pop("command")
    for name, path in dev_paths.get_added_paths().items():
        yield RichCompletion(name, description=path)
    yield from ENVS
    for path in _find_proj_path(command.prefix, str.startswith):
        yield RichCompletion(path.name, description=str(path))


def dev(
    name: tp.cast(str, Argument(nargs="?", completer=proj_name_completer)),
    add=False,
    ls=False,
        clean=False,
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
    clean
        remove paths that no longer exists

    Notes
    -----
        One can use `register_project` function to register custom_callbacks to run on cd to project path

    Examples
    -------
        > $PROJECT_PATHS = ["~/src/"]
        > dev proj-name # --> will cd into ~/src/proj-name
        > dev --add
    """

    if clean:
        dev_paths.clean_paths()
    elif add:
        _add_current_path()
    elif ls or (name is None):
        _list_cmds()
    else:
        added_paths = dev_paths.get_added_paths()
        if name in ENVS:
            ENVS[name]()
        elif name in added_paths:
            path = added_paths[name]
            if os.path.exists(path):
                return _start_proj_shell(Path(path))
            else:
                # old/expired link
                added_paths.pop(name)
                dev_paths.update_saved(*tuple(added_paths.values()))

        return _start_proj_shell(name)


if __name__ == "__main__":
    from xonsh.main import setup

    setup(
        env=[
            ("PROJECT_PATHS", ["~/src"]),
        ]
    )
    print(list(_find_proj_path("", str.startswith)))
