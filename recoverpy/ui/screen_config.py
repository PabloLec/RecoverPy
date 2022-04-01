from py_cui import PyCUI

from recoverpy.config import config as CONFIG
from recoverpy.ui import handler as handler
from recoverpy.ui.screen import Screen
from recoverpy.utils.logger import LOGGER
from recoverpy.utils.saver import SAVER


class ConfigScreen(Screen):
    """Display and edit RecoverPy configuration."""

    def __init__(self, master: PyCUI):
        super().__init__(master)
        self._log_enabled: bool = LOGGER.log_enabled
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
            self.master.show_error_popup("Path invalid", "Given save path is invalid.")
            return

        CONFIG.write_config_to_file(
            save_path=user_input,
            log_path=LOGGER.log_path,
            enable_logging=LOGGER.log_enabled,
        )

        self.master.show_message_popup("", "Save path changed successfully")

    def set_log_path(self):
        user_input: str = self.log_path_box.get()
        if not CONFIG.is_path_valid(user_input):
            self.master.show_error_popup("Path invalid", "Given log path is invalid.")
            return

        CONFIG.write_config_to_file(
            save_path=SAVER.save_path,
            log_path=user_input,
            enable_logging=LOGGER.log_enabled,
        )

        self.master.show_message_popup("", "Log path changed successfully")

    def enable_logging(self):
        if self._log_enabled:
            return

        self.set_log_state(enabled=True)
        self.master.show_message_popup("", "Logging enabled")

    def disable_logging(self):
        if not self._log_enabled:
            return

        self.set_log_state(enabled=False)
        self.master.show_message_popup("", "Logging disabled")

    def set_log_state(self, enabled: bool):
        self._log_enabled = enabled
        self.set_yes_no_colors()

    def save_all(self):
        save_path: str = self.save_path_box.get()
        log_path: str = self.log_path_box.get()
        if not CONFIG.is_path_valid(save_path):
            self.master.show_error_popup("Path invalid", "Given save path is invalid.")
            return
        if not CONFIG.is_path_valid(log_path):
            self.master.show_error_popup("Path invalid", "Given Log path is invalid.")
            return

        CONFIG.write_config_to_file(
            save_path=save_path,
            log_path=log_path,
            enable_logging=self._log_enabled,
        )
        handler.SCREENS_HANDLER.go_back()
