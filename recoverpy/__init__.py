from logging import getLogger
from recoverpy.config.setup import setup
from recoverpy.config.config import load_config
from recoverpy.views_handler import VIEWS_HANDLER

getLogger(__name__)


def main():
    """Set configuration and start UI."""
    setup()
    load_config()
    VIEWS_HANDLER.open_view_parameters()
