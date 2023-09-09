"""Main app class."""
from typing import Dict, cast

from textual.app import App
from textual.screen import Screen

from recoverpy.log.logger import log
from recoverpy.ui.css import get_css
from recoverpy.ui.screens.screen_modal import ModalScreen
from recoverpy.ui.screens.screen_params import ParamsScreen
from recoverpy.ui.screens.screen_path_edit import PathEditScreen
from recoverpy.ui.screens.screen_result import ResultScreen
from recoverpy.ui.screens.screen_save import SaveScreen
from recoverpy.ui.screens.screen_search import SearchScreen


class RecoverpyApp(App[None]):
    screens: Dict[str, Screen[None]]
    CSS_PATH = get_css()  # type: ignore[assignment]

    def __init__(self, *args, **kwargs) -> None:  # type: ignore
        super().__init__(*args, **kwargs)
        self._is_user_root = True
        self.load_screens()
        log.debug("app - Recoverpy app initialized")

    def load_screens(self) -> None:
        self.screens = {
            "params": ParamsScreen(name="params"),
            "search": SearchScreen(name="search"),
            "result": ResultScreen(name="result"),
            "save": SaveScreen(name="save"),
            "path_edit": PathEditScreen(name="path_edit"),
            "modal": ModalScreen(name="modal"),
        }
        for screen in self.screens:
            self.install_screen(self.screens[screen], screen)
            log.debug(f"app - Installed screen {screen}")

    def on_mount(self) -> None:
        if self._is_user_root:
            self.push_screen("params")
        else:
            log.warn("app - User is not root")
            cast(ModalScreen, self.get_screen("modal")).set(
                message="You must be root to run this app", callback=self.exit
            )
            self.push_screen("modal")

    async def on_params_screen_continue(self, message: ParamsScreen.Continue) -> None:
        log.info("app - User clicked continue on parameters screen")
        self.pop_screen()
        await self.push_screen("search")
        self.get_screen("search").post_message(
            SearchScreen.Start(message.searched_string, message.selected_partition)
        )

    async def on_search_screen_open(self, message: SearchScreen.Open) -> None:
        log.info("app - User clicked open on search screen")
        await self.push_screen("result")
        cast(ResultScreen, self.get_screen("result")).set(
            message.partition, message.block_size, message.inode
        )

    async def on_save_screen_saved(self, message: SaveScreen.Saved) -> None:
        log.info("app - User clicked save on save screen")
        cast(ModalScreen, self.get_screen("modal")).set(
            f"Saved results to {message.save_path}"
        )
        await self.push_screen("modal")
