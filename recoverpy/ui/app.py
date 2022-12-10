from textual.app import App

from ui.screens.screen_search_params import SearchParamsScreen

from ui.css import get_css


class RecoverPyApp(App):
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]
    SCREENS = {"params": SearchParamsScreen()}
    CSS_PATH = get_css()

    def on_mount(self) -> None:
        self.push_screen("params")
