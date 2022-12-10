from textual.app import App

from ui.screens.screen_search_params import SearchParamsScreen



class RecoverPyApp(App):
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]
    SCREENS = {"params": SearchParamsScreen()}

    def on_mount(self) -> None:
        self.push_screen("params")