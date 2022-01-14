<p align="center">
Useful xonsh-shell commands/alias/completer functions
</p>

## Installation

To install use pip:

``` bash
xpip install xontrib-commands
# or: xpip install -U git+https://github.com/jnoortheen/xontrib-commands
```

## Usage

``` bash
xontrib load commands
```

## building alias

Use [`xontrib_commands.Command`](https://github.com/jnoortheen/xontrib-commands/blob/main/xontrib/commands.py#L9) 
to build [arger](https://github.com/jnoortheen/arger) dispatcher
for your functions.

```py
from xontrib_commands import Command
@Command.reg
def record_stats(pkg_name=".", path=".local/stats.txt"):
    stat = $(scc @(pkg_name))
    echo @($(date) + stat) | tee -a @(path)
```

Now a full CLI is ready
```sh
$ record-stats --help                                                                        
usage: xonsh [-h] [-p PKG_NAME] [-a PATH]

optional arguments:
  -h, --help            show this help message and exit
  -p PKG_NAME, --pkg-name PKG_NAME
  -a PATH, --path PATH
```

## Commands

- The following commands are available once the xontrib is loaded.

### 1. reload-mods

```
usage: reload-mods [-h] name

Reload any python module in the current xonsh session.
Helpful during development.

positional arguments:
  name        Name of the module/package to reload. Giving partial names matches all the nested modules.

optional arguments:
  -h, --help  show this help message and exit

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

```  
          

### 2. report-key-bindings

```
usage: report-key-bindings [-h]

Show current Prompt-toolkit bindings in a nice table format

optional arguments:
  -h, --help  show this help message and exit

```  
          

### 3. dev

```
dev v1.0.0 (nuclear v1.1.10) - A command to cd into a directory. (Default action)

Usage:
dev [COMMAND] [OPTIONS] [NAME]

Arguments:
   [NAME] - name of the folder to cd into. This searches for names under $PROJECT_PATHS or the ones registered with ``dev add``

Options:
  --help [SUBCOMMANDS...] - Display this help and exit

Commands:
  add           - Register the current folder to dev command.
                  When using this, it will get saved in a file, also that is used during completions.
  ls            - Show currently registered paths
  load-env FILE - Load environment variables from the given file into Xonsh session
                  
                  Using https://github.com/theskumar/python-dotenv

Run "dev COMMAND --help" for more information on a command.

```  
          
