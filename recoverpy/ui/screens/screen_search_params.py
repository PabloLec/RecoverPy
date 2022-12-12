from textual._types import MessageTarget
from textual.app import ComposeResult
from textual.message import Message
from textual.screen import Screen
from textual.widgets import Input, Button, Label

from ui.widgets.partition_list import PartitionList


class SearchParamsScreen(Screen):
    _partition_list = None
    _search_input = None

    class Continue(Message):
        def __init__(self, sender: MessageTarget, search_text: str, selected_partition: str) -> None:
            self.search_text = search_text
            self.selected_partition = selected_partition
            super().__init__(sender)

    def compose(self) -> ComposeResult:
        self._partition_list = PartitionList()
        self._search_input = Input(name="search", placeholder="Search")

        yield Label("Type a text to search for:")
        yield self._search_input
        yield Label("Available partitions:")
        yield self._partition_list
        yield Button(label="Start search", id="start-search-button")

    async def on_button_pressed(self) -> None:
        search_text = self._search_input.value.strip()
        if len(search_text) == 0:
            # TODO: show error message
            pass
        selected_partition = self._partition_list.highlighted_child

        await self.app.post_message(self.Continue(self, search_text, selected_partition))

