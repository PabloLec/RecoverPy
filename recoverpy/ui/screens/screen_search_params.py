from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Input, Button, Label

from ui.widgets.partition_list import PartitionList


class SearchParamsScreen(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Pop screen")]

    def compose(self) -> ComposeResult:
        yield Label("Type a text to search for:")
        yield Input(name="search", placeholder="Search")
        yield Label("Available partitions:")
        yield PartitionList()
        yield Button(label="Start search", id="start-search-button")
