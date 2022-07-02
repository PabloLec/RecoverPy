from enum import Enum
from types import ModuleType
from typing import Dict

from recoverpy.ui.contents import (
    screen_block_content,
    screen_config_content,
    screen_parameters_content,
    screen_search_content,
)


class ScreenType(Enum):
    PARAMS = "ParametersScreen"
    CONFIG = "ConfigScreen"
    SEARCH = "SearchScreen"
    BLOCK = "BlockScreen"


SCREEN_TYPE_TO_CONTENT: Dict[ScreenType, ModuleType] = {
    ScreenType.PARAMS: screen_parameters_content,
    ScreenType.CONFIG: screen_config_content,
    ScreenType.SEARCH: screen_search_content,
    ScreenType.BLOCK: screen_block_content,
}


def init_ui(screen):
    for screen_type in SCREEN_TYPE_TO_CONTENT:
        if screen_type.value in str(type(screen)):
            SCREEN_TYPE_TO_CONTENT[screen_type].set(screen)
            return
    raise ValueError(f"Unknown screen type: {type(screen)}")
