from logging import getLogger
from os import environ

from recoverpy.config.config import parse_configuration
from recoverpy.views_handler import VIEWS_HANDLER as _VIEWS_HANDLER

getLogger(__name__)


def verify_terminal_conf():
    """Fix for older terminals."""
    term = environ["TERM"]

    if term != "xterm-256color":
        environ["TERM"] = "xterm-256color"


def main():
    """Set configuration and start UI."""
    verify_terminal_conf()
    parse_configuration()

    _VIEWS_HANDLER.open_view_parameters()
