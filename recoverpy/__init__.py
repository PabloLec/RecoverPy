from logging import getLogger
from os import environ

from recoverpy.config.config import load_config
from recoverpy.utils.helper import is_installed
from recoverpy.views_handler import VIEWS_HANDLER

getLogger(__name__)


def verify_terminal_conf():
    """Fix for older terminals."""
    term = environ["TERM"]

    if term != "xterm-256color":
        environ["TERM"] = "xterm-256color"


def verify_dependencies():
    """Verify the availability of mandatory dependencies.

    Raises:
        OSError: If a dependency is missing.
    """
    for dep in ["grep", "dd", "lsblk"]:
        if not is_installed(command=dep):
            raise OSError(
                f"Command '{dep}' is unavailable on your system.\n"
                "Please verify your configuration."
            )


def main():
    """Set configuration and start UI."""
    verify_dependencies()
    verify_terminal_conf()
    load_config()

    VIEWS_HANDLER.open_view_parameters()
