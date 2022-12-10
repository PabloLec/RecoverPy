from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Input

from ui.widgets.partition_list import PartitionList


class SearchParamsScreen(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Pop screen")]

    def compose(self) -> ComposeResult:
        yield Input(name="search", placeholder="Search")
        yield PartitionList()
