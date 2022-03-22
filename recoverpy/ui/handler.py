from typing import Dict, Final, Type

from py_cui import PyCUI

from recoverpy.ui import screen_block, screen_config, screen_parameters, screen_search


class ScreensHandler:
    """Provide ui navigation logic."""

    SCREENS_CLASSES: Final[Dict[str, Type]] = {
        "parameters": screen_parameters.ParametersScreen,
        "config": screen_config.ConfigScreen,
        "search": screen_search.SearchScreen,
        "results": screen_block.BlockScreen,
    }

    def __init__(self):
        self.screens: Dict[str, PyCUI] = {}
        self.init_screens()
        self.current_screen: str = None
        self.previous_screen: str = None

    def init_screens(self):
        for screen in self.SCREENS_CLASSES:
            self.screens[screen] = None

    def create_screen(self) -> PyCUI:
        screen: PyCUI = PyCUI(10, 10)
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
