from py_cui import PyCUI

from recoverpy.config import config as CONFIG
from recoverpy.utils.logger import LOGGER
from recoverpy.utils.saver import SAVER


class ConfigView:
    def __init__(self, master: PyCUI):
        self.master = master
        self.create_ui_content()
        self._log.enabled = LOGGER.log_enabled

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
            initial_text=SAVER.save_path,
        )
        self.master.add_button(
            "Save",
            row=3,
            column=8,
            row_span=1,
            column_span=1,
            padx=0,
            pady=0,
            command=None,
        ).set_color(1)
        self.master.add_label(
            title="Enable Logging",
            row=4,
            column=4,
            row_span=1,
            column_span=2,
            padx=0,
            pady=0,
        )
        self.yes_button = self.master.add_button(
            "Yes",
            row=5,
            column=3,
            row_span=1,
            column_span=1,
            padx=0,
            pady=0,
            command=None,
        )
        self.no_button = self.master.add_button(
            "No",
            row=5,
            column=6,
            row_span=1,
            column_span=1,
            padx=0,
            pady=0,
            command=None,
        )
        self.master.add_button(
            "Save & Exit",
            row=8,
            column=2,
            row_span=1,
            column_span=2,
            padx=0,
            pady=0,
            command=None,
        ).set_color(4)
        self.master.add_button(
            "Cancel",
            row=8,
            column=6,
            row_span=1,
            column_span=2,
            padx=0,
            pady=0,
            command=None,
        ).set_color(2)

    def set_save_path(self):
        user_input = self.save_path_box.get()
        if not CONFIG.path_is_valid(path=user_input):
            self.master.show_error_popup("Path invalid", "Given save path is invalid.")
            return

        CONFIG.write_config(
            save_path=user_input,
            log_path=LOGGER.log_file_path,
            log_enabled=LOGGER.log_enabled,
        )
