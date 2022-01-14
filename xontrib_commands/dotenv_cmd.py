from xonsh.built_ins import XSH


def load_env(
    file=".env",
):
    """Load environment variables from dotenv files

    Uses https://github.com/theskumar/python-dotenv

    Parameters
    ----------
    file
        Path to the dotenv file
    """
    if not XSH.env:
        return

    from dotenv import dotenv_values

    vals = dotenv_values(file)

    for name, val in vals.items():
        print(f"Setting {name}")
        XSH.env[name] = val
