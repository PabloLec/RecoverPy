"""First screen displayed to the user.
Allows user to enter search string and select partition."""

from typing import Generator, Optional

from textual.app import ComposeResult
from textual.containers import Container
from textual.message import Message
from textual.screen import Screen
from textual.widgets import Button, Checkbox, Input, Label

from recoverpy.log.logger import log
from recoverpy.models.partition import Partition
from recoverpy.ui.widgets.partition_list import PartitionList


class ParamsScreen(Screen[None]):
    _partition_list: Optional[PartitionList] = None

    class Continue(Message):
        def __init__(self, searched_string: str, selected_partition: str) -> None:
            super().__init__()
            self.searched_string = searched_string
            self.selected_partition = selected_partition

    def compose(self) -> ComposeResult:
        self._search_input = Input(
            name="search", id="search-input", placeholder="Search"
        )
        self._start_search_button = Button(
            label="Start search", id="start-search-button", disabled=True, variant="primary"
        )

        yield Label("Type a text to search for:")
        yield self._search_input
        yield Label("Available partitions:")
        yield from self._yield_partition_list()
        yield Container(self._start_search_button, Checkbox("Filter partitions", True))
        log.debug("params - Parameters screen composed")

    def _yield_partition_list(self) -> Generator[PartitionList, None, None]:
        if not self._partition_list:
            self._partition_list = PartitionList()
        yield self._partition_list

    async def on_button_pressed(self) -> None:
        if not self._partition_list:
            log.warning("Partition list not initialized")
            self.notify("Partition list is not available yet.", severity="warning")
            return

        highlighted_child = self._partition_list.highlighted_child
        searched_string = self._search_input.value.strip()

        if highlighted_child is None:
            log.warning("No partition selected for search")
            self.notify("Select a partition before starting search.", severity="warning")
            return

        if not searched_string:
            log.warning("No search string entered")
            self.notify("Enter a search string before starting search.", severity="warning")
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

    async def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        if self._partition_list:
            self._partition_list.set_partitions(event.value)
