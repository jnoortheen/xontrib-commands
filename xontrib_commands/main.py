from xonsh.built_ins import XonshSession


def _load_xontrib_(xsh: XonshSession, **_):
    from xontrib_commands.argerize import Command

    # register aliases
    from xontrib_commands.cmds import report_keys
    from xontrib_commands.cmds import parallex
    from xontrib_commands.cmds import reload
    from xontrib_commands.cmds import dotenv_cmd
    from xontrib_commands.cmds import dev_cmd

    Command.reg_no_thread(reload.reload_mods)
    Command.reg_no_thread(report_keys.report_key_bindings)
    Command.reg_no_thread(dev_cmd.dev)
    Command.reg_no_thread(dotenv_cmd.load_env)
    Command.reg_no_thread(parallex.parallex)
