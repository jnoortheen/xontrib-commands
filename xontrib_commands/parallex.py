from typing import List
import sys
from xonsh.built_ins import XSH


async def run_sp_parallel(
    *commands: str, shell=False, order_out=True, show_running=True
):
    import asyncio
    import asyncio.subprocess as asp
    import shlex

    def print_cmd(cmd):
        sys.stderr.buffer.write(f"  $ {cmd}\n".encode())
        sys.stderr.flush()

    async def run(cmd, capture=False):
        kwargs = dict(env=XSH.env.detype())
        if capture:
            kwargs["stdout"] = asp.PIPE
            kwargs["stderr"] = asp.PIPE
        if show_running and not capture:
            print_cmd(cmd)
        if shell:
            proc = await asp.create_subprocess_shell(cmd, **kwargs)
        else:
            program, *args = shlex.split(cmd)
            proc = await asp.create_subprocess_exec(program, *args, **kwargs)
        if capture:
            stdout, stderr = await proc.communicate()
            if show_running:
                print_cmd(cmd)
            sys.stdout.buffer.write(stdout)
            sys.stdout.flush()
            sys.stderr.buffer.write(stderr)
            sys.stderr.flush()
            return proc.returncode
        else:
            return await proc.wait()

    def prepare_cmds():
        for idx, cmd in enumerate(commands):
            # first command is not captured and will have tty
            is_first = idx != 0
            yield run(cmd, capture=is_first and order_out)

    return await asyncio.gather(*tuple(prepare_cmds()))


def parallex(
    args: List[str],
    shell=False,
    no_order=False,
    hide_cmd=False,
):
    """Execute multiple subprocess in parallel

    Parameters
    ----------
    args :
        individual commands need to be quoted and passed as separate arguments
    shell :
        each command should be run with system's commands
    no_order :
        commands output are interleaved and not ordered
    hide_cmd:
        do not print the running command
    Examples
    --------
    running linters in parallel
        $ parallex "flake8 ." "mypy xonsh"
    """
    import asyncio

    order_out = not no_order
    results = asyncio.run(
        run_sp_parallel(
            *args,
            shell=shell,
            order_out=no_order,
            show_running=(order_out and (not hide_cmd)),
        )
    )
    if any(results):
        sys.exit(1)
