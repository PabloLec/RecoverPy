"""Screen displaying search results."""

from asyncio import Task, create_task

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.screen import Screen
from textual.timer import Timer
from textual.widgets import Button, Label

from recoverpy.lib.search.search_engine import SearchEngine
from recoverpy.lib.storage.block_device_metadata import DeviceIOError
from recoverpy.log.logger import log
from recoverpy.models.search_result import SearchResult
from recoverpy.ui.widgets.search_result_list import SearchResultList


class SearchScreen(Screen[None]):
    BINDINGS = [
        Binding("o", "open_result", "Open result"),
        Binding("p", "toggle_pause", "Pause/resume"),
        Binding("q", "exit_screen", "Exit"),
    ]

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
        self._progress_timer: Timer | None = None
        self._consumer_task: Task[None] | None = None
        self._search_error_notified = False
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        self._search_result_list = SearchResultList()
        self._search_status_label = Label("Waiting...", id="search-status")
        self._result_count_label = Label("0", id="result-count")
        self._progress_title_label = Label("- progress -", id="progress-title")
        self._progress_label = Label("0.00%", id="progress")
        self._open_button = Button(
            label="Open", id="open-button", disabled=True, variant="primary"
        )
        self._pause_button = Button(
            label="Pause", id="pause-button", disabled=True, variant="default"
        )

        yield self._search_result_list
        yield Vertical(
            self.InfoContainer(self._progress_title_label),
            self.InfoContainer(self._progress_label),
            self.InfoContainer(Label("- status -", id="status-title")),
            self.InfoContainer(self._search_status_label),
            self.InfoContainer(Label("- result count -", id="result-count-title")),
            self.InfoContainer(self._result_count_label),
            id="info-bar",
        )
        yield self._open_button
        yield self._pause_button
        yield Button("Exit", id="exit-button", variant="error")
        log.debug("search - Search screen composed")

    async def on_search_screen_start(self, message: Start) -> None:
        self._search_error_notified = False
        try:
            self.search_engine = SearchEngine(
                message.selected_partition, message.searched_string
            )
        except DeviceIOError as error:
            log.error(f"search - {error}")
            self.notify(error.user_message, severity="error")
            self.app.pop_screen()
            return
        self._search_status_label.update("Searching...")
        self._pause_button.disabled = False
        self._pause_button.label = "Pause"
        self.set_focus(self._search_result_list)
        await self._start_search_engine()

    async def _start_search_engine(self) -> None:
        await self.search_engine.start_search()
        # UI consumes formatted results asynchronously while scan workers run
        # in background threads managed by SearchEngine.
        self._consumer_task = create_task(
            self._search_result_list.start_consumer(
                self.search_engine.formatted_results_queue
            )
        )
        self._progress_timer = self.set_interval(0.1, self._update_progress_labels)

    def _update_progress_labels(self) -> None:
        if self.search_engine.search_progress.error_message:
            self._search_status_label.update("Failed")
            if not self._search_error_notified:
                self._search_error_notified = True
                self.notify(
                    self.search_engine.search_progress.error_message,
                    severity="error",
                )
            if self._progress_timer:
                self._progress_timer.stop()
                self._progress_timer = None

        self._result_count_label.update(
            str(self.search_engine.search_progress.result_count)
        )
        self._progress_label.update(
            f"{self.search_engine.search_progress.progress_percent:.2f}%"
        )
        if self.search_engine.is_paused():
            self._search_status_label.update("Paused")
        elif int(self.search_engine.search_progress.progress_percent) < 100:
            self._search_status_label.update("Searching...")
        if int(self.search_engine.search_progress.progress_percent) >= 100:
            self._search_status_label.update("Completed")
            self._pause_button.disabled = True
            if self._progress_timer:
                self._progress_timer.stop()
                self._progress_timer = None

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        actions = {
            "exit-button": self._handle_exit_button,
            "open-button": self._handle_open_button,
            "pause-button": self._handle_pause_button,
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
        selected_search_result = self._get_selected_search_result()
        log.info(f"search - Opening inode {selected_search_result.inode}")
        self.app.post_message(
            self.Open(
                selected_search_result.inode,
                self.search_engine.search_params.block_size,
                self.search_engine.search_params.partition,
            )
        )

    async def _handle_pause_button(self) -> None:
        if self.search_engine.is_paused():
            self.search_engine.resume_search()
            self._pause_button.label = "Pause"
            self._search_status_label.update("Searching...")
        else:
            self.search_engine.pause_search()
            self._pause_button.label = "Resume"
            self._search_status_label.update("Paused")

    def _get_selected_search_result(self) -> SearchResult:
        return self._search_result_list.search_results[
            self._search_result_list.get_index()
        ]

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

    async def action_open_result(self) -> None:
        await self._handle_open_button()

    async def action_exit_screen(self) -> None:
        await self._handle_exit_button()

    async def action_toggle_pause(self) -> None:
        if hasattr(self, "search_engine"):
            await self._handle_pause_button()

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        if action == "open_result" and self._open_button.disabled:
            return None
        if action == "toggle_pause" and (
            not hasattr(self, "search_engine") or self._pause_button.disabled
        ):
            return None
        return True
