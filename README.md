<p align="center">
Useful xonsh-shell commands/alias functions
</p>

<p align="center">
If you like the idea click ⭐ on the repo and stay tuned.
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

Use [`xontrib.commands.Command`](https://github.com/jnoortheen/xontrib-commands/blob/main/xontrib/commands.py#L9) 
to build [arger](https://github.com/jnoortheen/arger) dispatcher
for your functions.

```py
from xontrib.commands import Command
@Command
def record_stats(pkg_name=".", path=".local/stats.txt"):
    stat = $(scc @(pkg_name))
    echo @($(date) + stat) | tee -a @(path)
```

## Commands

### 1. reload-mods
![](./docs/2020-12-02-14-30-47.png)

### 2. report-key-bindggs
![](./docs/2020-12-02-14-30-17.png)

## Credits

This package was created with [xontrib cookiecutter template](https://github.com/jnoortheen/xontrib-cookiecutter).
