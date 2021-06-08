import py_cui

from recoverpy import view_parameters as PARAMETERS_VIEW
from recoverpy import view_search as SEARCH_VIEW
from recoverpy import view_results as RESULTS_VIEW


_PARAMETERS_VIEW = None
_SEARCH_VIEW = None
_RESULTS_VIEW = None


def open_view_parameters():
    """Starts a ParametersView instance."""
    global _PARAMETERS_VIEW

    _PARAMETERS_VIEW = py_cui.PyCUI(10, 10)
    _PARAMETERS_VIEW.toggle_unicode_borders()
    _PARAMETERS_VIEW.set_title("Retrieve deleted or overwritten text files")
    PARAMETERS_VIEW.ParametersView(_PARAMETERS_VIEW)
    _PARAMETERS_VIEW.start()


def close_view_parameters():
    """Stops the global ParametersView instance."""
    global _PARAMETERS_VIEW

    _PARAMETERS_VIEW.stop()


def open_view_search(partition: str, string_to_search: str):
    """Starts a SearchView instance."""
    global _SEARCH_VIEW

    _SEARCH_VIEW = py_cui.PyCUI(10, 10)
    _SEARCH_VIEW.toggle_unicode_borders()
    _SEARCH_VIEW.set_title("View and explore found files")
    SEARCH_VIEW.SearchView(_SEARCH_VIEW, partition=partition, string_to_search=string_to_search)
    _SEARCH_VIEW.start()


def close_view_search():
    """Stops the global SearchView instance."""
    global _SEARCH_VIEW

    _SEARCH_VIEW.stop()


def open_view_results(partition: str, block: str):
    global _RESULTS_VIEW

    _RESULTS_VIEW = py_cui.PyCUI(10, 10)
    _RESULTS_VIEW.toggle_unicode_borders()
    _RESULTS_VIEW.set_title("")
    RESULTS_VIEW.ResultsView(_RESULTS_VIEW, partition=partition, initial_block=block)
    _RESULTS_VIEW.start()
