"""Screen displaying grep results."""

from asyncio import ensure_future, sleep
from typing import List

from textual._types import MessageTarget
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.screen import Screen
from textual.widgets import Button, Label

from recoverpy.lib.search.search_engine import SearchEngine
from recoverpy.ui.widgets.grep_result_list import GrepResultList


class SearchScreen(Screen):
    _grep_result_list: GrepResultList
    _result_count_label: Label
    _progress_title_label: Label
    _progress_label: Label
    _open_button: Button
    search_engine: SearchEngine

    class Start(Message):
        def __init__(
            self, sender: MessageTarget, searched_string: str, selected_partition: str
        ) -> None:
            self.searched_string = searched_string
            self.selected_partition = selected_partition
            super().__init__(sender)

    class Open(Message):
        def __init__(
            self, sender: MessageTarget, inode: int, block_size: int, partition: str
        ) -> None:
            self.inode = inode
            self.block_size = block_size
            self.partition = partition
            super().__init__(sender)

    class InfoContainer(Horizontal):
        def __init__(self, *args, **kwargs) -> None:  # type: ignore
            super().__init__(classes="info-container", *args, **kwargs)

    def __init__(self, *args, **kwargs) -> None:  # type: ignore
        self.results: List[str] = []
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        self._grep_result_list = GrepResultList()
        self._result_count_label = Label("0", id="result-count")
        self._progress_title_label = Label("", id="progress-title")
        self._progress_label = Label("", id="progress")
        self._open_button = Button(label="Open", id="open-button", disabled=True)

        yield self._grep_result_list
        yield Vertical(
            self.InfoContainer(Label("- result count -", id="result-count-title")),
            self.InfoContainer(self._result_count_label),
            self.InfoContainer(self._progress_title_label),
            self.InfoContainer(self._progress_label),
            id="info-bar",
        )
        yield self._open_button
        yield Button("Exit", id="exit-button")

    async def on_search_screen_start(self, message: Start) -> None:
        self.search_engine = SearchEngine(
            message.selected_partition, message.searched_string
        )
        while self._grep_result_list not in self.visible_widgets:
            continue
        await self.search_engine.start_search()
        ensure_future(
            self._grep_result_list.start_consumer(self.search_engine.list_items_queue)
        )
        ensure_future(self.get_progress())

    async def get_progress(self) -> None:
        while True:
            self._result_count_label.update(
                str(self.search_engine.search_progress.result_count)
            )
            if self.search_engine.search_progress.progress_percent != 0.0:
                if self._progress_title_label.renderable == "":
                    self._progress_title_label.update("- progress -")
                self._progress_label.update(
                    f"{self.search_engine.search_progress.progress_percent}%"
                )
            await sleep(0.1)

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "exit-button":
            self.search_engine.stop_search()
            self.app.exit()
            exit()
        elif button_id == "open-button":
            await self.app.post_message(
                self.Open(
                    self,
                    self._grep_result_list.grep_results[
                        self._grep_result_list.index
                    ].inode,
                    self.search_engine.search_params.block_size,
                    self.search_engine.search_params.partition,
                )
            )

    async def on_list_view_highlighted(self) -> None:
        self._open_button.disabled = False
