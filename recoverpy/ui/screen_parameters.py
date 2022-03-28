from re import findall

from py_cui import PyCUI

from recoverpy.ui import handler
from recoverpy.ui.screen import Screen
from recoverpy.utils import helper
from recoverpy.utils.logger import LOGGER


class ParametersScreen(Screen):
    """Select a partion and type a string to search."""

    def __init__(self, master: PyCUI):
        super().__init__(master)

        self.partition_to_search: str
        self.string_to_search: str
        self.partitions_dict: dict

        helper.is_user_root(window=self.master)
        self.create_ui_content()
        self.get_system_partitions()

    def get_system_partitions(self):
        self.partitions_dict = helper.get_partitions()
        if not self.partitions_dict:
            LOGGER.write("Error", "No partition found !")
            self.master.show_error_popup("Hum...", "No partition found.")
            return

        self.add_partitions_to_list()

    def add_partitions_to_list(self):
        if self.partitions_dict is None:
            return

        for partition in self.partitions_dict:
            if self.partitions_dict[partition]["IS_MOUNTED"]:
                self.partitions_list_scroll_menu.add_item(
                    f"Name: {partition}  -  "
                    f"Type: {self.partitions_dict[partition]['FSTYPE']}  -  "
                    f"Mounted at: {self.partitions_dict[partition]['MOUNT_POINT']}"
                )
            else:
                self.partitions_list_scroll_menu.add_item(
                    f"Name: {partition}  -  "
                    f"Type: {self.partitions_dict[partition]['FSTYPE']}"
                )

            LOGGER.write("debug", f"Partition added to list: {partition}")

    def select_partition(self):
        selected_partition = findall(
            r"Name\:\ ([^\ \n]+)\ ",
            self.partitions_list_scroll_menu.get(),
        )[0]

        if self.partitions_dict[selected_partition]["IS_MOUNTED"]:
            # Warn the user to unmount his partition before searching in it
            self.master.show_warning_popup(
                "You probably should unmount first !",
                f"It is highly recommended to unmount {selected_partition}"
                " ASAP to avoid any data loss.",
            )
        else:
            self.master.show_message_popup(
                "",
                f"Partition {selected_partition} selected.",
            )

        self.partition_to_search = f"/dev/{selected_partition.strip()}"

        LOGGER.write(
            "info",
            f"Partition selected: {self.partition_to_search}",
        )

    def confirm_search(self):
        if not helper.is_user_root(window=self.master):
            return

        self.string_to_search = self.string_text_box.get()

        if self.partition_to_search == "":
            # No partition selected
            self.master.show_message_popup(
                "Whoops !",
                "You have to select a partition to search.",
            )
            LOGGER.write("warning", "No partition selected for search")
        elif not self.string_to_search.strip():
            # Blank string to search
            self.master.show_message_popup(
                "Oops !",
                "You have to enter a text to search.",
            )
            LOGGER.write("warning", "No string given for search")
        else:
            # Prompt to confirm string
            self.master.show_yes_no_popup(
                "Do you want to search this text on partition "
                f"{self.partition_to_search} ?",
                self.start_search,
            )

    def start_search(self, is_confirmed: bool):
        if is_confirmed:
            LOGGER.write("info", "Starting search")
            handler.SCREENS_HANDLER.open_screen(
                "search",
                partition=self.partition_to_search,
                string_to_search=self.string_to_search.strip(),
            )
