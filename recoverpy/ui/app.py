"""
Defines the RecoverpyApp class which serves as the main app orchestrator for the application.
"""

from typing import Dict, cast

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Footer

from recoverpy.lib.env_check import verify_app_environment
from recoverpy.log.logger import log
from recoverpy.ui.css import get_css
from recoverpy.ui.screens.modal import install_and_push_modal
from recoverpy.ui.screens.screen_params import ParamsScreen
from recoverpy.ui.screens.screen_path_edit import PathEditScreen
from recoverpy.ui.screens.screen_result import ResultScreen
from recoverpy.ui.screens.screen_save import SaveScreen
from recoverpy.ui.screens.screen_search import SearchScreen


class RecoverpyApp(App[None]):
    screens: Dict[str, Screen[None]]
    CSS_PATH = get_css()  # type: ignore[assignment]
    BINDINGS = [
        Binding(
            "question_mark",
            "show_keyboard_help",
            "Help",
            key_display="?",
            priority=True,
        ),
        Binding("ctrl+q", "quit", "Quit"),
    ]

    def __init__(self, *args, **kwargs) -> None:  # type: ignore
        super().__init__(*args, **kwargs)
        self._is_user_root = False
        self._initialize_screens()
        log.debug("Recoverpy app initialized")

    def _initialize_screens(self) -> None:
        self.screens = {
            "params": ParamsScreen(name="params"),
            "search": SearchScreen(name="search"),
            "result": ResultScreen(name="result"),
            "save": SaveScreen(name="save"),
            "path_edit": PathEditScreen(name="path_edit"),
        }
        for screen_name, screen_instance in self.screens.items():
            self.install_screen(screen_instance, screen_name)
            log.debug(f"Installed screen {screen_name}")

    def compose(self) -> ComposeResult:
        yield Footer()

    async def on_mount(self) -> None:
        self.theme = "atom-one-dark"
        await self.push_screen("params")
        await verify_app_environment(self)
        self.notify("Press ? for keyboard help", title="Tip", timeout=5)

    def _get_keyboard_help_message(self) -> str:
        hidden_keys = {"left", "right", "up", "down"}
        lines: list[str] = []
        for active_binding in self.active_bindings.values():
            binding = active_binding.binding
            if not binding.show or not binding.description:
                continue
            if binding.key in hidden_keys:
                continue
            key = binding.key_display or binding.key
            lines.append(f"{key}: {binding.description}")

        if not lines:
            return "No keyboard shortcuts available."

        ordered = sorted(set(lines), key=str.lower)
        return "Available shortcuts:\n" + "\n".join(ordered)

    async def action_show_keyboard_help(self) -> None:
        if self.screen.name == "keyboard-help-modal":
            return
        await install_and_push_modal(
            self,
            name="keyboard-help-modal",
            message=self._get_keyboard_help_message()
            + "\n\nTip: Use Tab / Shift+Tab to move focus.",
        )

    async def on_params_screen_continue(self, message: ParamsScreen.Continue) -> None:
        log.info("User clicked continue on parameters screen")
        await self.push_screen("search")
        self.get_screen("search").post_message(
            SearchScreen.Start(message.searched_string, message.selected_partition)
        )

    async def on_search_screen_open(self, message: SearchScreen.Open) -> None:
        log.info("User clicked open on search screen")
        await self.push_screen("result")
        cast(ResultScreen, self.get_screen("result")).set(
            message.partition, message.block_size, message.inode
        )

    async def on_save_screen_saved(self, message: SaveScreen.Saved) -> None:
        log.info("User clicked save on save screen")
        await self._display_save_modal(message.save_path)

    async def _display_save_modal(self, save_path: str) -> None:
        await install_and_push_modal(
            self, "save-modal", f"Saved results to {save_path}"
        )
