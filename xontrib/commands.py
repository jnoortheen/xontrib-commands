from xontrib_commands.utils import Command

# register aliases
from xontrib_commands import reload, report_keys, dev_cmd, dotenv_cmd

Command.reg_no_thread(reload.reload_mods)
Command.reg_no_thread(report_keys.report_key_bindings)
Command.reg_no_thread(dev_cmd.dev)
Command.reg_no_thread(dotenv_cmd.load_env)
