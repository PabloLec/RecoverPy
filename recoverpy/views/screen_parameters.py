from re import findall

from py_cui import GREEN_ON_BLACK, YELLOW_ON_BLACK, PyCUI, keys

from recoverpy import screens
from recoverpy.utils import helper
from recoverpy.utils.logger import LOGGER


class ParametersView:
    """ParametersView prompts to select a partion and a string to search.

    User is prompted to select a partition and a string to search in it.

    Attributes:
        partition_to_search (str): Partition selected by user.
        string_to_search (str): String entered by user.
        partitions_dict (dict): Dictionnary of system partitions found with
            lsblk command and their attributes.
    """

    def __init__(self, master: PyCUI):
        """Initialize ParametersView.

        Args:
            master (PyCUI): PyCUI main object for UI
        """
        self.master = master

        self.partition_to_search = None
        self.string_to_search = None
        self.partitions_dict = None

        LOGGER.write("info", "Starting 'ParametersView' CUI window")
        helper.is_user_root(window=self.master)

        self.create_ui_content()
        self.get_system_partitions()
        self.add_partitions_to_list()

    def create_ui_content(self):
        """Handle the creation of the UI elements."""
        self.partitions_list_scroll_menu = self.master.add_scroll_menu(
            "Select a partition to search:", 0, 0, row_span=9, column_span=5
        )
        self.partitions_list_scroll_menu.add_key_command(
            keys.KEY_ENTER, self.select_partition
        )

        # Color rules
        self.partitions_list_scroll_menu.add_text_color_rule(
            "Mounted at",
            YELLOW_ON_BLACK,
            "contains",
        )
        self.partitions_list_scroll_menu.set_selected_color(GREEN_ON_BLACK)

        self.string_text_box = self.master.add_text_block(
            "Enter a text to search:",
            0,
            5,
            row_span=9,
            column_span=5,
        )

        self.confirm_search_button = self.master.add_button(
            "Start",
            9,
            4,
            row_span=1,
            column_span=2,
            padx=0,
            pady=0,
            command=self.confirm_search,
        )
        self.confirm_search_button.set_color(4)

        self.open_config_button = self.master.add_button(
            "Settings",
            9,
            8,
            row_span=1,
            column_span=2,
            padx=1,
            pady=0,
            command=screens.SCREENS_HANDLER.open_screen_config,
        )
        self.open_config_button.set_color(1)

    def get_system_partitions(self):
        """Call lsblk and lsblk output formatting."""
        partitions_list = helper.lsblk()
        self.partitions_dict = helper.format_partitions_list(
            window=self.master,
            raw_lsblk=partitions_list,
        )

    def add_partitions_to_list(self):
        """Populate the partition list with lsblk output."""
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
        """Handle the user selection of a partition in the list."""
        selected_partition = findall(
            r"Name\:\ ([^\ \n]+)\ ",
            self.partitions_list_scroll_menu.get(),
        )[0]

        if self.partitions_dict[selected_partition]["IS_MOUNTED"]:
            # Warn the user to unmount his partition first
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

        self.partition_to_search = "/dev/" + selected_partition.strip()

        LOGGER.write(
            "info",
            f"Partition selected: {self.partition_to_search}",
        )

    def confirm_search(self):
        """Check if partition is selected and string is given.
        If all required elements are present, launch start_search method.
        """
        if not helper.is_user_root(window=self.master):
            return

        self.string_to_search = self.string_text_box.get()

        LOGGER.write("info", "Starting search")

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
        """Close parameters screen and open search screen if confirmed.

        Args:
            is_confirmed (bool): User popup selection
        """
        if is_confirmed:
            screens.SCREENS_HANDLER.close_screen_parameters()
            screens.SCREENS_HANDLER.open_screen_search(
                partition=self.partition_to_search,
                string_to_search=self.string_to_search.strip(),
            )
