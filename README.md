# xontrib-commands

Useful xonsh-shell commands/alias/completer functions

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

Use [`xontrib_commands.argerize:Command`](https://github.com/jnoortheen/xontrib-commands/blob/1bf016e08f192478c6322b2a859ae48567372bdb/xontrib_commands/argerize.py#L21) 
to build [arger](https://github.com/jnoortheen/arger) dispatcher
for your functions. This will create a nice alias function with auto-completions support.

```py
from xontrib_commands.argerize import Command

@Command.reg
def record_stats(pkg_name=".", path=".local/stats.txt"):
    stat = $(scc @(pkg_name))
    echo @($(date) + stat) | tee -a @(path)
```

- Directly passing the `Arger` instances is also supported. 

```py
from xontrib_commands.argerize import Arger, Command

arger = Arger(prog="tst", description="App Description goes here")

@arger.add_cmd
def create(name: str):
    """Create new test.

    :param name: Name of the test
    """
    print(locals())

@arger.add_cmd
def remove(*name: str):
    """Remove a test with variadic argument.

    :param name: tests to remove
    """
    print(locals())

Command.reg(arger)
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
dev - A command to cd into a directory. (Default action)

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

### 4. parallex

```
usage: parallex [-h] [-s] [-n] [-c] [args ...]

Execute multiple subprocess in parallel

positional arguments:
  args  individual commands need to be quoted and passed as separate arguments

options:
  -h, --help
                        show this help message and exit
  -s, --shell
                        each command should be run with system's commands
  -n, --no-order
                        commands output are interleaved and not ordered
  -c, --hide-cmd
                        do not print the running command

Examples
--------
running linters in parallel
    $ parallex "flake8 ." "mypy xonsh"
```
