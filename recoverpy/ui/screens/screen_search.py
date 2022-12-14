from textual._types import MessageTarget
from textual.app import ComposeResult
from textual.message import Message
from textual.screen import Screen

from lib.search.search_engine import SearchEngine
from textual.widgets import Label


class SearchScreen(Screen):
    search_engine: SearchEngine

    class Start(Message):
        def __init__(self, sender: MessageTarget, searched_string: str, selected_partition: str) -> None:
            self.searched_string = searched_string
            self.selected_partition = selected_partition
            super().__init__(sender)

    def compose(self) -> ComposeResult:
        yield Label("Type a text to search for:")
        print("coucou")
        print(self._pending_message)

    def on_search_screen_start(self, message: Start) -> None:
        print("ON_START")
        self.search_engine = SearchEngine(message.selected_partition, message.searched_string)
        self.search_engine.start_search()
