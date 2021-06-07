import py_cui

from recoverpy import view_parameters as PARAMETERS_MENU
from recoverpy import view_search as SEARCH_MENU
from recoverpy import view_results as BLOCK_MENU


_PARAMETERS_MENU = None
_SEARCH_MENU = None
_BLOCK_MENU = None


def open_view_parameters():
    """Starts a ParametersView instance."""
    global _PARAMETERS_MENU

    _PARAMETERS_MENU = py_cui.PyCUI(10, 10)
    _PARAMETERS_MENU.toggle_unicode_borders()
    _PARAMETERS_MENU.set_title("Retrieve deleted or overwritten text files")
    PARAMETERS_MENU.ParametersView(_PARAMETERS_MENU)
    _PARAMETERS_MENU.start()


def close_view_parameters():
    """Stops the global ParametersView instance."""
    global _PARAMETERS_MENU

    _PARAMETERS_MENU.stop()


def open_view_search(partition: str, string_to_search: str):
    """Starts a SearchView instance."""
    global _SEARCH_MENU

    _SEARCH_MENU = py_cui.PyCUI(10, 10)
    _SEARCH_MENU.toggle_unicode_borders()
    _SEARCH_MENU.set_title("View and explore found files")
    SEARCH_MENU.SearchView(_SEARCH_MENU, partition=partition, string_to_search=string_to_search)
    _SEARCH_MENU.start()


def close_view_search():
    """Stops the global SearchView instance."""
    global _SEARCH_MENU

    _SEARCH_MENU.stop()


def open_view_results(partition: str, block: str):
    global _BLOCK_MENU

    _BLOCK_MENU = py_cui.PyCUI(10, 10)
    _BLOCK_MENU.toggle_unicode_borders()
    _BLOCK_MENU.set_title("")
    BLOCK_MENU.ResultsView(_BLOCK_MENU, partition=partition, initial_block=block)
    _BLOCK_MENU.start()
