from xonsh.built_ins import XonshSession


def _load_xontrib_(xsh: XonshSession, **_):
    from xontrib_commands.argerize import Command

    # register aliases
    from xontrib_commands import reload, report_keys, dev_cmd, dotenv_cmd, parallex

    Command.reg_no_thread(reload.reload_mods)
    Command.reg_no_thread(report_keys.report_key_bindings)
    Command.reg_no_thread(dev_cmd.dev)
    Command.reg_no_thread(dotenv_cmd.load_env)
    Command.reg_no_thread(parallex.parallex)
