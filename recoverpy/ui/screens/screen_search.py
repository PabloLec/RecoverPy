import asyncio
from asyncio import ensure_future, to_thread, get_event_loop

from textual._types import MessageTarget
from textual.app import ComposeResult
from textual.message import Message
from textual.screen import Screen

from lib.search.search_engine import SearchEngine
from textual.scrollbar import ScrollDown
from textual.widgets import Label

from ui.widgets.grep_result_list import GrepResultList


class SearchScreen(Screen):
    _grep_result_list: GrepResultList
    search_engine: SearchEngine

    class Start(Message):
        def __init__(self, sender: MessageTarget, searched_string: str, selected_partition: str) -> None:
            self.searched_string = searched_string
            self.selected_partition = selected_partition
            super().__init__(sender)

    def __init__(
            self,
            name: str | None = None,
            id: str | None = None,
            classes: str | None = None,
    ):
        super().__init__(name, id, classes)
        self.results = []

    def compose(self) -> ComposeResult:
        self._grep_result_list = GrepResultList()
        yield Label("Type a text to search for:")
        yield self._grep_result_list

    async def on_search_screen_start(self, message: Start) -> None:
        self.search_engine = SearchEngine(message.selected_partition, message.searched_string)
        while self._grep_result_list not in self.visible_widgets:
            continue
        await self.search_engine.start_search(self, self.progress_callback)

    async def on_new_results(self, message: SearchEngine.NewResults) -> None:
        for result in message.results.lines:
            get_event_loop().create_task(self._grep_result_list.append(result))
    async def progress_callback(self, progress: int):
        print("PROGRESS:", progress)
