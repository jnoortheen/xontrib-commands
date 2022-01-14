from xontrib_commands.utils import Command

# register aliases
from xontrib_commands import reload, report_keys, dev_cmd, dotenv_cmd

Command.reg(reload.reload_mods)
Command.reg(report_keys.report_key_bindings)
Command.reg(dev_cmd.dev)
Command.reg(dotenv_cmd.load_env)
