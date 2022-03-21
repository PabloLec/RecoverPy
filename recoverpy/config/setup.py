from os import environ
from recoverpy.utils.helper import is_installed


def verify_terminal_conf():
    """Fix for older terminals."""
    term = environ["TERM"]

    if term != "xterm-256color":
        environ["TERM"] = "xterm-256color"


def verify_dependencies():
    needed_dependencies: list = ["grep", "dd", "lsblk"]
    for dep in needed_dependencies:
        if not is_installed(command=dep):
            raise OSError(
                f"Command '{dep}' is unavailable on your system.\n"
                "Please verify your configuration."
            )


def setup():
    verify_dependencies()
    verify_terminal_conf()
