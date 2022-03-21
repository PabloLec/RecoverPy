from py_cui import PyCUI

from recoverpy import screen_handler as screen_handler
from recoverpy.config import config as CONFIG
from recoverpy.screens.screen import Screen
from recoverpy.utils.logger import LOGGER
from recoverpy.utils.saver import SAVER


class ConfigScreen(Screen):
    """ConfigScreen is used to display and edit configuration.

    Attributes:
        _log_enabled (bool): Mirror LOGGER state for button colorization
    """

    def __init__(self, master: PyCUI):
        """Initialize ConfigScreen.

        Args:
            master (PyCUI): PyCUI main object for UI.
        """
        super().__init__(master)
        self._log_enabled = LOGGER.log_enabled
        self.create_ui_content()

    def create_ui_content(self):
        """Handle the creation of the UI elements."""
        self.save_path_box = self.master.add_text_box(
            title="Save Path",
            row=0,
            column=1,
            row_span=1,
            column_span=8,
            padx=0,
            pady=0,
            initial_text=SAVER.save_path,
        )
        self.master.add_button(
            "Save",
            row=1,
            column=8,
            row_span=1,
            column_span=1,
            padx=0,
            pady=0,
            command=self.set_save_path,
        ).set_color(1)
        self.log_path_box = self.master.add_text_box(
            title="Log Path",
            row=2,
            column=1,
            row_span=1,
            column_span=8,
            padx=0,
            pady=0,
            initial_text=LOGGER.log_path,
        )
        self.master.add_button(
            "Save",
            row=3,
            column=8,
            row_span=1,
            column_span=1,
            padx=0,
            pady=0,
            command=self.set_log_path,
        ).set_color(1)
        self.master.add_label(
            title="Enable Logging",
            row=4,
            column=4,
            row_span=1,
            column_span=2,
            padx=0,
            pady=0,
        ).selectable = False
        self.yes_button = self.master.add_button(
            "Yes",
            row=5,
            column=3,
            row_span=1,
            column_span=1,
            padx=0,
            pady=0,
            command=self.enable_logging,
        )
        self.no_button = self.master.add_button(
            "No",
            row=5,
            column=6,
            row_span=1,
            column_span=1,
            padx=0,
            pady=0,
            command=self.disable_logging,
        )
        self.master.add_button(
            "Save & Exit",
            row=8,
            column=2,
            row_span=1,
            column_span=2,
            padx=0,
            pady=0,
            command=self.save_all,
        ).set_color(4)
        self.master.add_button(
            "Cancel",
            row=8,
            column=6,
            row_span=1,
            column_span=2,
            padx=0,
            pady=0,
            command=screen_handler.SCREENS_HANDLER.go_back,
        ).set_color(2)

        self.set_yes_no_colors()

    def set_save_path(self):
        """Verify and set provided save path."""
        user_input = self.save_path_box.get()
        if not CONFIG.path_is_valid(path=user_input):
            self.master.show_error_popup("Path invalid", "Given save path is invalid.")
            return

        CONFIG.write_config(
            save_path=user_input,
            log_path=LOGGER.log_path,
            enable_logging=LOGGER.log_enabled,
        )

        self.master.show_message_popup("", "Save path changed successfully")

    def set_log_path(self):
        """Verify and set provided log path."""
        user_input = self.log_path_box.get()
        if not CONFIG.path_is_valid(path=user_input):
            self.master.show_error_popup("Path invalid", "Given log path is invalid.")
            return

        CONFIG.write_config(
            save_path=SAVER.save_path,
            log_path=user_input,
            enable_logging=LOGGER.log_enabled,
        )

        self.master.show_message_popup("", "Log path changed successfully")

    def enable_logging(self):
        """Enable logging on button press."""
        if self._log_enabled:
            return

        self.set_log_state(enabled=True)
        self.master.show_message_popup("", "Logging enabled")

    def disable_logging(self):
        """Disable logging on button press."""
        if not self._log_enabled:
            return

        self.set_log_state(enabled=False)
        self.master.show_message_popup("", "Logging disabled")

    def set_log_state(self, enabled: bool):
        """Set disared log state.

        Args:
            enabled (bool): Logging enabled or disabled
        """
        self._log_enabled = enabled
        CONFIG.write_config(
            save_path=SAVER.save_path,
            log_path=LOGGER.log_path,
            enable_logging=self._log_enabled,
        )
        self.set_yes_no_colors()

    def set_yes_no_colors(self):
        """Colorize log state buttons."""
        if self._log_enabled:
            self.yes_button.set_color(4)
            self.no_button.set_color(1)
        else:
            self.yes_button.set_color(1)
            self.no_button.set_color(4)

    def save_all(self):
        """Save full config and go back to first menu."""
        save_path = self.save_path_box.get()
        log_path = self.log_path_box.get()
        if not CONFIG.path_is_valid(path=save_path):
            self.master.show_error_popup("Path invalid", "Given save path is invalid.")
            return
        if not CONFIG.path_is_valid(path=log_path):
            self.master.show_error_popup("Path invalid", "Given Log path is invalid.")
            return

        CONFIG.write_config(
            save_path=save_path,
            log_path=log_path,
            enable_logging=self._log_enabled,
        )
        screen_handler.SCREENS_HANDLER.go_back()
