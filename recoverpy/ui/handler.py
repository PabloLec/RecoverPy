from typing import Dict, Type

from py_cui import PyCUI

from recoverpy.ui import (
    screen,
    screen_block,
    screen_config,
    screen_parameters,
    screen_search,
)


class ScreensHandler:
    """Provide ui navigation logic."""

    SCREENS_CLASSES: Dict[str, Type] = {
        "parameters": screen_parameters.ParametersScreen,
        "config": screen_config.ConfigScreen,
        "search": screen_search.SearchScreen,
        "block": screen_block.BlockScreen,
    }

    def __init__(self):
        self.screens: Dict[str, screen.Screen] = {}
        self.init_screens()
        self.current_screen: str = None
        self.previous_screen: str = None

    def init_screens(self):
        for screen_class in self.SCREENS_CLASSES:
            self.screens[screen_class] = None

    def create_py_cui_master(self) -> PyCUI:
        master: PyCUI = PyCUI(10, 10)
        master.toggle_unicode_borders()
        master.set_title("RecoverPy 1.5.0")

        return master

    def open_screen(self, screen_name: str, **kwargs):
        self.close_screen(self.current_screen)

        master = self.create_py_cui_master()
        created_screen_object = self.SCREENS_CLASSES[screen_name](master, **kwargs)
        self.screens[screen_name] = created_screen_object

        self.current_screen, self.previous_screen = (
            screen_name,
            self.current_screen,
        )

        created_screen_object.master.start()

    def close_screen(self, screen_name: str):
        if screen_name is None or self.screens[screen_name] is None:
            return
        self.screens[screen_name].master.stop()

    def go_back(self):
        self.close_screen(self.current_screen)
        self.current_screen, self.previous_screen = (
            self.previous_screen,
            self.current_screen,
        )
        self.screens[self.current_screen].master._stopped = False
        self.screens[self.current_screen].master.start()


SCREENS_HANDLER: ScreensHandler = ScreensHandler()
