from logging import getLogger

from recoverpy.config.config import load_config
from recoverpy.config.setup import setup
from recoverpy.ui.handler import SCREENS_HANDLER
from recoverpy.ui.widgets.screen_type import ScreenType

getLogger(__name__)


def main():
    """Set configuration and start UI."""
    setup()
    load_config()
    SCREENS_HANDLER.open_screen(ScreenType.PARAMS)
