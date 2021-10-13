from py_cui import PyCUI

from recoverpy.views import view_config, view_parameters, view_results, view_search


class ViewsHandler:
    """Store UI windows instances and provide navigation logic.

    Attributes:
        _parameters_view_window (PyCUI): Parameters window.
        _config_view_window  (PyCUI): Config window.
        _search_view_window (PyCUI): Search window.
        _results_view_window (PyCUI): Results window.
    """

    def __init__(self):
        """Initialize ViewsHandler."""
        self._parameters_view_window = None
        self._config_view_window = None
        self._search_view_window = None
        self._results_view_window = None

    def create_view(self):
        """Create a PyCUI instance with standard attributes.

        Returns:
            PyCUI: Created view
        """
        view = PyCUI(10, 10)
        view.toggle_unicode_borders()
        view.set_title("RecoverPy 1.3.2")

        return view

    def open_view_parameters(self):
        """Start a ParametersView instance."""
        self._parameters_view_window = self.create_view()

        view_parameters.ParametersView(self._parameters_view_window)
        self._parameters_view_window.start()

    def close_view_parameters(self):
        """Stop the ParametersView instance."""
        if self._parameters_view_window is None:
            return
        self._parameters_view_window.stop()

    def open_view_config(self):
        """Start a ConfigView instance."""
        self._config_view_window = self.create_view()

        view_config.ConfigView(self._config_view_window)
        self._config_view_window.start()

    def close_view_config(self):
        """Stop the ParametersView instance."""
        if self._config_view_window is None:
            return
        self._config_view_window.stop()

    def open_view_search(self, partition: str, string_to_search: str):
        """Start a SearchView instance.

        Args:
            partition (str): Selected system partition
            string_to_search (str): String to be searched
        """
        self.close_view_results()
        self._search_view_window = self.create_view()

        view_search.SearchView(
            self._search_view_window,
            partition=partition,
            string_to_search=string_to_search,
        )
        self._search_view_window.start()

    def close_view_search(self):
        """Stop the SearchView instance."""
        if self._search_view_window is None:
            return
        self._search_view_window.stop()

    def open_view_results(self, partition: str, block: str):
        """Start a ResultsView instance.

        Args:
            partition (str): Selected system partition
            block (str): Block to be displayed
        """
        self.close_view_search()
        self._results_view_window = self.create_view()
        view_results.ResultsView(
            self._results_view_window,
            partition=partition,
            initial_block=block,
        )
        self._results_view_window.start()

    def close_view_results(self):
        """Stop the ResultsView instance."""
        if self._results_view_window is None:
            return
        self._results_view_window.stop()

    def results_go_back(self):
        """Go back from results view to search view."""
        self.close_view_results()
        self._search_view_window._stopped = False
        self._search_view_window.start()


VIEWS_HANDLER = ViewsHandler()
