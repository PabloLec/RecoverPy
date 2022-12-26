from textual.app import App
from textual.reactive import Reactive

from recoverpy.ui.css import get_css
from recoverpy.ui.screens.screen_modal import ModalScreen
from recoverpy.ui.screens.screen_params import ParamsScreen
from recoverpy.ui.screens.screen_path_edit import PathEditScreen
from recoverpy.ui.screens.screen_result import ResultScreen
from recoverpy.ui.screens.screen_save import SaveScreen
from recoverpy.ui.screens.screen_search import SearchScreen


class RecoverpyApp(App):
    SCREENS = {
        "params": ParamsScreen(),
        "search": SearchScreen(),
        "result": ResultScreen(),
        "save": SaveScreen(),
        "path_edit": PathEditScreen(),
        "modal": ModalScreen(),
    }
    CSS_PATH = get_css()

    def on_mount(self) -> None:
        self.dark = Reactive(True)
        self.push_screen("params")

    async def on_params_screen_continue(self, message: ParamsScreen.Continue) -> None:
        self.pop_screen()
        await self.push_screen("search")
        await self.get_screen("search").post_message(
            SearchScreen.Start(
                self, message.searched_string, message.selected_partition
            )
        )

    async def on_search_screen_open(self, message: SearchScreen.Open) -> None:
        self.get_screen("result").set(
            message.partition, message.block_size, message.inode
        )
        await self.push_screen("result")

    async def on_save_screen_saved(self, message: SaveScreen.Saved) -> None:
        self.get_screen("modal").set_message(f"Saved results to {message.save_path}")
        await self.push_screen("modal")
