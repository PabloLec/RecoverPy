"""Screen displaying grep results."""

from asyncio import Task, create_task
from typing import List

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.screen import Screen
from textual.timer import Timer
from textual.widgets import Button, Label

from recoverpy.lib.search.search_engine import SearchEngine
from recoverpy.log.logger import log
from recoverpy.models.grep_result import GrepResult
from recoverpy.ui.widgets.grep_result_list import GrepResultList


class SearchScreen(Screen[None]):
    class Start(Message):
        def __init__(self, searched_string: str, selected_partition: str) -> None:
            super().__init__()
            self.searched_string = searched_string
            self.selected_partition = selected_partition

    class Open(Message):
        def __init__(self, inode: int, block_size: int, partition: str) -> None:
            super().__init__()
            self.inode = inode
            self.block_size = block_size
            self.partition = partition

    class InfoContainer(Horizontal):
        def __init__(self, *args, **kwargs) -> None:  # type: ignore
            super().__init__(classes="info-container", *args, **kwargs)

    def __init__(self, *args, **kwargs) -> None:  # type: ignore
        self.results: List[str] = []
        self._progress_timer: Timer | None = None
        self._consumer_task: Task[None] | None = None
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
        log.debug("search - Search screen composed")

    async def on_search_screen_start(self, message: Start) -> None:
        self.search_engine = SearchEngine(
            message.selected_partition, message.searched_string
        )
        self.set_focus(self._grep_result_list)
        await self._start_search_engine()

    async def _start_search_engine(self) -> None:
        await self.search_engine.start_search()
        self._consumer_task = create_task(
            self._grep_result_list.start_consumer(
                self.search_engine.formatted_results_queue
            )
        )
        self._progress_timer = self.set_interval(0.1, self._update_progress_labels)

    def _update_progress_labels(self) -> None:
        self._result_count_label.update(
            str(self.search_engine.search_progress.result_count)
        )
        self._update_progress_percent_title()

    def _update_progress_percent_title(self) -> None:
        if int(self.search_engine.search_progress.progress_percent) == 0:
            return

        if str(self._progress_title_label.content) == "":
            self._progress_title_label.update("- progress -")

        self._progress_label.update(
            f"{self.search_engine.search_progress.progress_percent}%"
        )

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        actions = {
            "exit-button": self._handle_exit_button,
            "open-button": self._handle_open_button,
        }

        button_id = event.button.id
        if button_id in actions:
            await actions[button_id]()

    async def _handle_exit_button(self) -> None:
        log.info("search - User clicked exit button")
        self.search_engine.stop_search()
        self.app.exit()
        exit()

    async def _handle_open_button(self) -> None:
        log.info("search - User clicked open button")
        selected_grep_result = self._get_selected_grep_result()
        log.info(f"search - Opening inode {selected_grep_result.inode}")
        self.app.post_message(
            self.Open(
                selected_grep_result.inode,
                self.search_engine.search_params.block_size,
                self.search_engine.search_params.partition,
            )
        )

    def _get_selected_grep_result(self) -> GrepResult:
        return self._grep_result_list.grep_results[self._grep_result_list.get_index()]

    async def on_list_view_highlighted(self) -> None:
        self._open_button.disabled = False

    def on_unmount(self) -> None:
        if self._progress_timer:
            self._progress_timer.stop()
            self._progress_timer = None
        if self._consumer_task:
            self._consumer_task.cancel()
            self._consumer_task = None
        if hasattr(self, "search_engine"):
            self.search_engine.stop_search()
