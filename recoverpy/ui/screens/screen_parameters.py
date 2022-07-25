from re import findall
from typing import Optional

from py_cui import PyCUI
from py_cui.widgets import ScrollMenu, ScrollTextBlock

from recoverpy.lib import helper
from recoverpy.ui import handler, strings
from recoverpy.ui.screens.screen import Screen
from recoverpy.ui.widgets.screen_type import ScreenType


class ParametersScreen(Screen):
    """Select a partion and type a string to search."""

    def __init__(self, master: PyCUI):
        super().__init__(master)

        self.partitions_list_scroll_menu: Optional[ScrollMenu] = None
        self.string_text_box: Optional[ScrollTextBlock] = None

        self.partition_to_search: Optional[str] = None
        self.string_to_search: Optional[str] = None
        self.partitions_dict: Optional[dict] = None

        helper.is_user_root(window=self.master)
        self.create_ui_content()
        self.get_system_partitions()

    def get_system_partitions(self):
        self.partitions_dict = helper.get_partitions()
        if not self.partitions_dict:
            self.master.show_error_popup(
                strings.title_generic_error, strings.content_no_partition
            )
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

    def select_partition(self):
        selected_partition = findall(
            r"Name: ([^ \n]+) ",
            self.partitions_list_scroll_menu.get(),
        )[0]

        if self.partitions_dict[selected_partition]["IS_MOUNTED"]:
            # Warn the user to unmount his partition before searching in it
            self.master.show_warning_popup(
                strings.title_unmount, strings.content_unmount
            )
        else:
            self.master.show_message_popup(
                strings.title_empty,
                f"{strings.content_partition_selected}: {selected_partition}",
            )

        self.partition_to_search = f"/dev/{selected_partition.strip()}"

    def confirm_search(self):
        if not helper.is_user_root(window=self.master):
            return

        self.string_to_search = self.string_text_box.get()
        if not hasattr(self, "partition_to_search") or self.partition_to_search == "":
            # No partition selected
            self.master.show_message_popup(
                strings.title_generic_error,
                strings.content_no_partition_selected,
            )
        elif not self.string_to_search.strip():
            # Blank string to search
            self.master.show_message_popup(
                strings.title_generic_error,
                strings.content_no_text_entered,
            )
        else:
            # Prompt to confirm string
            self.master.show_yes_no_popup(
                f"{strings.title_confirm_search} {self.partition_to_search} ?",
                self.start_search,
            )

    def start_search(self, is_confirmed: bool):
        if is_confirmed and self.string_to_search:
            handler.SCREENS_HANDLER.open_screen(
                ScreenType.SEARCH,
                partition=self.partition_to_search,
                string_to_search=self.string_to_search.strip(),
            )
