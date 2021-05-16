import py_cui

from recoverpy import parameters_menu as PARAMETERS_MENU
from recoverpy import search_menu as SEARCH_MENU
from recoverpy import block_menu as BLOCK_MENU


_PARAMETERS_MENU = None
_SEARCH_MENU = None
_BLOCK_MENU = None


def open_parameters_menu():
    """Starts a ParametersMenu instance."""
    global _PARAMETERS_MENU

    _PARAMETERS_MENU = py_cui.PyCUI(10, 10)
    _PARAMETERS_MENU.toggle_unicode_borders()
    _PARAMETERS_MENU.set_title("Retrieve deleted or overwritten text files")
    PARAMETERS_MENU.ParametersMenu(_PARAMETERS_MENU)
    _PARAMETERS_MENU.start()


def close_parameters_menu():
    """Stops the global ParametersMenu instance."""
    global _PARAMETERS_MENU

    _PARAMETERS_MENU.stop()


def open_search_menu(partition: str, string_to_search: str):
    """Starts a SearchMenu instance."""
    global _SEARCH_MENU

    _SEARCH_MENU = py_cui.PyCUI(10, 10)
    _SEARCH_MENU.toggle_unicode_borders()
    _SEARCH_MENU.set_title("View and explore found files")
    SEARCH_MENU.SearchMenu(_SEARCH_MENU, partition=partition, string_to_search=string_to_search)
    _SEARCH_MENU.start()


def close_search_menu():
    """Stops the global SearchMenu instance."""
    global _SEARCH_MENU

    _SEARCH_MENU.stop()


def open_block_menu(partition: str, block: str):
    global _BLOCK_MENU

    _BLOCK_MENU = py_cui.PyCUI(10, 10)
    _BLOCK_MENU.toggle_unicode_borders()
    _BLOCK_MENU.set_title("")
    BLOCK_MENU.BlockMenu(_BLOCK_MENU, partition=partition, initial_block=block)
    _BLOCK_MENU.start()
