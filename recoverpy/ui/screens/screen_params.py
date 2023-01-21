"""First screen displayed to the user.
Allows user to enter search string and select partition."""

from textual._types import MessageTarget
from textual.app import ComposeResult
from textual.message import Message
from textual.screen import Screen
from textual.widgets import Button, Input, Label

from recoverpy.models.partition import Partition
from recoverpy.ui.widgets.partition_list import PartitionList


class ParamsScreen(Screen):
    _partition_list: PartitionList
    _search_input: Input
    _start_search_button: Button

    class Continue(Message):
        def __init__(
            self, sender: MessageTarget, searched_string: str, selected_partition: str
        ) -> None:
            self.searched_string = searched_string
            self.selected_partition = selected_partition
            super().__init__(sender)

    def compose(self) -> ComposeResult:
        self._partition_list = PartitionList()
        self._search_input = Input(name="search", placeholder="Search")
        self._start_search_button = Button(
            label="Start search", id="start-search-button", disabled=True
        )

        yield Label("Type a text to search for:")
        yield self._search_input
        yield Label("Available partitions:")
        yield self._partition_list
        yield self._start_search_button

    async def on_button_pressed(self) -> None:
        if self._partition_list.highlighted_child is None:
            return
        searched_string = self._search_input.value.strip()
        if len(searched_string) == 0:
            return
        selected_partition: Partition = self._partition_list.list_items[
            self._partition_list.highlighted_child.id
        ]
        await self.app.post_message(
            self.Continue(self, searched_string, selected_partition.get_full_name())
        )

    async def on_input_changed(self, event: Input.Changed) -> None:
        self._start_search_button.disabled = len(event.value.strip()) == 0
