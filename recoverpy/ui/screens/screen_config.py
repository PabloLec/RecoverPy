from typing import Optional

from py_cui import PyCUI
from py_cui.widgets import Button, ScrollTextBlock

from recoverpy.config import config as CONFIG
from recoverpy.lib.logger import Logger
from recoverpy.lib.saver import Saver
from recoverpy.ui import handler as handler
from recoverpy.ui import strings
from recoverpy.ui.screens.screen import Screen


class ConfigScreen(Screen):
    """Display and edit RecoverPy configuration."""

    def __init__(self, master: PyCUI):
        super().__init__(master)

        self.yes_button: Optional[Button] = None
        self.no_button: Optional[Button] = None
        self.save_path_box: Optional[ScrollTextBlock] = None
        self.log_path_box: Optional[ScrollTextBlock] = None

        self._log_enabled: bool = Logger().log_enabled
        self.create_ui_content()
        self.set_yes_no_colors()

    def set_yes_no_colors(self):
        if self._log_enabled:
            self.yes_button.set_color(4)
            self.no_button.set_color(1)
        else:
            self.yes_button.set_color(1)
            self.no_button.set_color(4)

    def set_save_path(self):
        user_input: str = self.save_path_box.get()
        if not CONFIG.is_path_valid(user_input):
            self.master.show_error_popup(
                strings.title_path_invalid, strings.content_save_path_invalid
            )
            return

        CONFIG.write_config_to_file(
            save_path=user_input,
            log_path=str(Logger().log_path),
            enable_logging=Logger().log_enabled,
        )

        self.master.show_message_popup(
            strings.title_empty, strings.content_save_path_changed
        )

    def set_log_path(self):
        user_input: str = self.log_path_box.get()
        if not CONFIG.is_path_valid(user_input):
            self.master.show_error_popup(
                strings.title_path_invalid, strings.content_log_path_invalid
            )
            return

        CONFIG.write_config_to_file(
            save_path=str(Saver().save_path),
            log_path=user_input,
            enable_logging=Logger().log_enabled,
        )

        self.master.show_message_popup(
            strings.title_empty, strings.content_log_path_changed
        )

    def enable_logging(self):
        if self._log_enabled:
            return

        self.set_log_state(enabled=True)
        self.master.show_message_popup(strings.title_empty, strings.content_log_enabled)

    def disable_logging(self):
        if not self._log_enabled:
            return

        self.set_log_state(enabled=False)
        self.master.show_message_popup(
            strings.title_empty, strings.content_log_disabled
        )

    def set_log_state(self, enabled: bool):
        self._log_enabled = enabled
        self.set_yes_no_colors()

    def save_all(self):
        save_path: str = self.save_path_box.get()
        log_path: str = self.log_path_box.get()
        if not CONFIG.is_path_valid(save_path):
            self.master.show_error_popup(
                strings.title_path_invalid, strings.content_save_path_changed
            )
            return
        if not CONFIG.is_path_valid(log_path):
            self.master.show_error_popup(
                strings.title_path_invalid, strings.content_log_path_changed
            )
            return

        CONFIG.write_config_to_file(
            save_path=save_path,
            log_path=log_path,
            enable_logging=self._log_enabled,
        )
        handler.SCREENS_HANDLER.go_back()
