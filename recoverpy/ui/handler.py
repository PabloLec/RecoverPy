from sys import exit
from typing import Dict, Type

from py_cui import PyCUI

from recoverpy.ui import (
    screen,
    screen_block,
    screen_config,
    screen_parameters,
    screen_search,
)
from recoverpy.ui.contents.screen_type import ScreenType


def create_py_cui_master() -> PyCUI:
    master: PyCUI = PyCUI(10, 10)
    master.toggle_unicode_borders()
    master.set_title("RecoverPy 1.5.1")
    master.run_on_exit(exit)

    return master


class ScreensHandler:
    """Provide ui navigation logic."""

    SCREENS_CLASSES: Dict[str, Type] = {
        ScreenType.PARAMS: screen_parameters.ParametersScreen,
        ScreenType.CONFIG: screen_config.ConfigScreen,
        ScreenType.SEARCH: screen_search.SearchScreen,
        ScreenType.BLOCK: screen_block.BlockScreen,
    }

    def __init__(self):
        self.screens: Dict[str, screen.Screen] = {}
        self.current_screen: str = ""
        self.previous_screen: str = ""

    def open_screen(self, screen_name: ScreenType, **kwargs):
        self.close_screen(self.current_screen)

        master = create_py_cui_master()
        created_screen_object = self.SCREENS_CLASSES[screen_name.value](
            master, **kwargs
        )
        self.screens[screen_name.value] = created_screen_object

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
        self.screens[self.current_screen].master.start()


SCREENS_HANDLER: ScreensHandler = ScreensHandler()
