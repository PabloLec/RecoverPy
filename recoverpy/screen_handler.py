from typing import Any, Dict, Final, Type
from py_cui import PyCUI

from recoverpy.screens import (
    screen_config,
    screen_parameters,
    screen_results,
    screen_search,
)


class ScreensHandler:
    """Provide navigation logic."""

    SCREENS_CLASSES: Final[Dict[str, Type]] = {
        "parameters": screen_parameters.ParametersScreen,
        "config": screen_config.ConfigScreen,
        "search": screen_search.SearchScreen,
        "results": screen_results.ResultsScreen,
    }

    def __init__(self):
        """Initialize ScreensHandler."""
        self.screens: Dict[str, Any] = {
            "parameters": None,
            "config": None,
            "search": None,
            "results": None,
        }
        self.current_screen = None
        self.previous_screen = None

    def create_screen(self):
        """Create a PyCUI instance with standard attributes.

        Returns:
            PyCUI: Created screen
        """
        screen = PyCUI(10, 10)
        screen.toggle_unicode_borders()
        screen.set_title("RecoverPy 1.5.0")

        return screen

    def open_screen(self, screen_name: str, **kwargs):
        self.current_screen, self.previous_screen = screen_name, self.current_screen
        self.close_screen(self.previous_screen)
        self.screens[screen_name] = self.create_screen()
        self.SCREENS_CLASSES[screen_name](self.screens[screen_name], **kwargs)
        self.screens[screen_name].start()

    def close_screen(self, screen_name):
        if screen_name is None:
            return
        self.screens[screen_name].stop()

    def go_back(self):
        self.close_screen(self.current_screen)
        self.current_screen, self.previous_screen = (
            self.previous_screen,
            self.current_screen,
        )
        self.screens[self.current_screen]._stopped = False
        self.screens[self.current_screen].start()


SCREENS_HANDLER = ScreensHandler()
