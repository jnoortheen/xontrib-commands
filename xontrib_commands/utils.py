from typing import Optional

from xonsh.built_ins import XSH


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
