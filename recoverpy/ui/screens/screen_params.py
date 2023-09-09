"""First screen displayed to the user.
Allows user to enter search string and select partition."""

from textual.app import ComposeResult
from textual.message import Message
from textual.screen import Screen
from textual.widgets import Button, Input, Label

from recoverpy.log.logger import log
from recoverpy.models.partition import Partition
from recoverpy.ui.widgets.partition_list import PartitionList


class ParamsScreen(Screen[None]):
    class Continue(Message):
        def __init__(self, searched_string: str, selected_partition: str) -> None:
            super().__init__()
            self.searched_string = searched_string
            self.selected_partition = selected_partition

    def compose(self) -> ComposeResult:
        self._partition_list = PartitionList()
        self._search_input = Input(
            name="search", id="search-input", placeholder="Search"
        )
        self._start_search_button = Button(
            label="Start search", id="start-search-button", disabled=True
        )

        yield Label("Type a text to search for:")
        yield self._search_input
        yield Label("Available partitions:")
        yield self._partition_list
        yield self._start_search_button
        log.debug("params - Parameters screen composed")

    async def on_button_pressed(self) -> None:
        highlighted_child = self._partition_list.highlighted_child
        searched_string = self._search_input.value.strip()

        if highlighted_child is None:
            log.warn("No partition selected for search")
            return

        if not searched_string:
            log.warn("No search string entered")
            return

        selected_partition: Partition = self._partition_list.list_items[
            highlighted_child.id
        ]

        log.info(
            f"User selected partition {selected_partition.get_full_name()} and search string `{searched_string}`"
        )

        self.app.post_message(
            self.Continue(searched_string, selected_partition.get_full_name())
        )

    async def on_input_changed(self, event: Input.Changed) -> None:
        self._start_search_button.disabled = len(event.value.strip()) == 0
