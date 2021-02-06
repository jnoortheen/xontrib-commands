import sys

from .utils import Command


@Command.reg
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

    modules = list(
        sys.modules
    )  # create a copy of names. so that it will not raise warning
    for mod_name in modules:
        mod = sys.modules[mod_name]
        if name and not mod_name.startswith(name):
            continue
        print("reload ", mod_name)
        try:
            importlib.reload(mod)
        except Exception as e:
            print("failed to reload", mod_name, e)
