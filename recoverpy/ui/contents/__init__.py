from types import ModuleType
from typing import Dict

from recoverpy.ui.contents import (
    screen_block_content,
    screen_config_content,
    screen_parameters_content,
    screen_search_content,
)

SCREEN_TYPE_MAP: Dict[str, ModuleType] = {
    "ParametersScreen": screen_parameters_content,
    "ConfigScreen": screen_config_content,
    "SearchScreen": screen_search_content,
    "BlockScreen": screen_block_content,
}


def init_ui(screen):
    for screen_type in SCREEN_TYPE_MAP:
        if screen_type in str(type(screen)):
            SCREEN_TYPE_MAP[screen_type].set(screen)
            return
    raise ValueError(f"Unknown screen type: {type(screen)}")
