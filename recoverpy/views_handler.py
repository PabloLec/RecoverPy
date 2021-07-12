import py_cui

from recoverpy.views import view_parameters as _PARAMETERS_VIEW
from recoverpy.views import view_search as _SEARCH_VIEW
from recoverpy.views import view_results as _RESULTS_VIEW


class ViewsHandler:
    """Store UI windows instances and provide navigation logic.

    Attributes:
        _parameters_view_window (py_cui.PyCUI): Parameters window.
        _search_view_window (py_cui.PyCUI): Search window.
        _results_view_window (py_cui.PyCUI): Results window.
    """

    def __init__(self):
        """Constructor for ViewsHandler."""

        _parameters_view_window = None
        _search_view_window = None
        _results_view_window = None

    def open_view_parameters(self):
        """Start a ParametersView instance."""

        self._parameters_view_window = py_cui.PyCUI(10, 10)
        self._parameters_view_window.toggle_unicode_borders()
        self._parameters_view_window.set_title("RecoverPy 1.3.0")
        _PARAMETERS_VIEW.ParametersView(self._parameters_view_window)
        self._parameters_view_window.start()

    def close_view_parameters(self):
        """Stop the ParametersView instance."""

        self._parameters_view_window.stop()

    def open_view_search(self, partition: str, string_to_search: str):
        """Start a SearchView instance."""

        self._search_view_window = py_cui.PyCUI(10, 10)
        self._search_view_window.toggle_unicode_borders()
        self._search_view_window.set_title("View and explore found files")
        _SEARCH_VIEW.SearchView(
            self._search_view_window,
            partition=partition,
            string_to_search=string_to_search,
        )
        self._search_view_window.start()

    def close_view_search(self):
        """Stop the SearchView instance."""

        self._search_view_window.stop()

    def open_view_results(self, partition: str, block: str):
        """Start a ResultsView instance."""

        self._results_view_window = py_cui.PyCUI(10, 10)
        self._results_view_window.toggle_unicode_borders()
        self._results_view_window.set_title("")
        _RESULTS_VIEW.ResultsView(
            self._results_view_window,
            partition=partition,
            initial_block=block,
        )
        self._results_view_window.start()


VIEWS_HANDLER = ViewsHandler()
