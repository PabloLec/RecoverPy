import asyncio
from asyncio import ensure_future, to_thread, get_event_loop
from time import sleep
from tkinter import Widget

from textual._types import MessageTarget
from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.events import Event
from textual.message import Message
from textual.screen import Screen

from lib.search.search_engine import SearchEngine
from textual.scrollbar import ScrollDown
from textual.widgets import Label, Button

from ui.widgets.grep_result_list import GrepResultList

from models.grep_result import GrepResult


class SearchScreen(Screen):
    _grep_result_list: GrepResultList
    _result_count_label: Label
    _progress_title_label: Label
    _progress_label: Label
    search_engine: SearchEngine

    class Start(Message):
        def __init__(self, sender: MessageTarget, searched_string: str, selected_partition: str) -> None:
            self.searched_string = searched_string
            self.selected_partition = selected_partition
            super().__init__(sender)

    class Open(Message):
        def __init__(self, sender: MessageTarget, grep_result: GrepResult) -> None:
            self.grep_result = grep_result
            super().__init__(sender)

    class InfoContainer(Horizontal):
        def __init__(self, *args, **kwargs):
            super().__init__(classes="info-container", *args, **kwargs)

    def __init__(self, *args, **kwargs):
        self.results = []
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        self._grep_result_list = GrepResultList()
        yield self._grep_result_list
        self._result_count_label = Label("0", id="result-count")
        self._progress_title_label = Label("", id="progress-title")
        self._progress_label = Label("", id="progress")
        yield Vertical(
            self.InfoContainer(Label("- result count -", id="result-count-title")),
            self.InfoContainer(self._result_count_label),
            self.InfoContainer(self._progress_title_label),
            self.InfoContainer(self._progress_label),
            id="info-bar",
        )
        yield Button("Open", id="open-button")
        yield Button("Exit", id="exit-button")

    async def on_search_screen_start(self, message: Start) -> None:
        self.search_engine = SearchEngine(message.selected_partition, message.searched_string)
        while self._grep_result_list not in self.visible_widgets:
            continue
        await self.search_engine.start_search()
        ensure_future(self._grep_result_list.start_consumer(self.search_engine.list_items_queue))
        ensure_future(self.get_progress())

    async def get_progress(self):
        while True:
            self._result_count_label.update(str(self.search_engine.search_progress.result_count))
            if self.search_engine.search_progress.progress_percent != 0.0:
                if self._progress_title_label.renderable == "":
                    self._progress_title_label.update("- progress -")
                self._progress_label.update(f"{self.search_engine.search_progress.progress_percent}%")
            await asyncio.sleep(0.1)

    async def on_button_pressed(self, event: Event) -> None:
        button_id = event.sender.id
        if button_id == "exit-button":
            self.search_engine.stop_search()
            self.app.exit()
            exit()
        elif button_id == "open-button":
            await self.app.post_message(self.Open(self, self._grep_result_list.grep_results[self._grep_result_list.index]))

