from queue import Queue
from re import findall
from shlex import quote
from time import sleep

from py_cui import BLACK_ON_GREEN, PyCUI, keys

from recoverpy import search
from recoverpy.screens import handler
from recoverpy.utils.logger import LOGGER
from recoverpy.utils.saver import SAVER
from recoverpy.screens.screen_with_block_display import MenuWithBlockDisplay


class SearchScreen(MenuWithBlockDisplay):
    """SearchScreen displays search results and corresponding block contents.

    Args:
        _BLOCK_DISPLAY_MENU (MenuWithBlockDisplay): Composition to inherit block display
        methods

    Attributes:
        master (PyCUI): PyCUI main object for UI
        queue_object (Queue): Queue object where grep command stdout will be stored
        result_index (int): Number of results already processed
        grep_progress (str): Formated output of 'progress' command
        partition (str): System partition selected by user for search
        block_size (int): Size of partition block for dd parsing
        searched_string (str): String given by the user that will be searched by dd
    """

    def __init__(self, master: PyCUI, partition: str, string_to_search: str):
        """Initialize SearchScreen.

        Args:
            master (PyCUI): PyCUI main object for UI
            partition (str): System partition to search
            string_to_search (str): String to search in partition blocks
        """
        super().__init__(master)

        self.queue_object = Queue()
        self.result_index = 0

        self.grep_progress = ""
        self.inodes = []
        self.partition = partition
        self.block_size = 512

        self.searched_string = string_to_search

        LOGGER.write("info", "Starting 'SearchScreen' CUI window")

        self.create_ui_content()

        search.start_search(self)

        LOGGER.write(
            "info",
            f"Raw searched string:\n{self.searched_string}",
        )
        LOGGER.write(
            "info",
            f"Formated searched string:\n{quote(self.searched_string)}",
        )

    def set_title(self):
        """Set window title based on number of results and search progress."""
        if self.grep_progress != "":
            title = f"{self.grep_progress} - {self.result_index} results"
        else:
            title = f"{self.result_index} results"

        self.master.set_title(title)

    def create_ui_content(self):
        """Handle the creation of the UI elements."""
        self.search_results_scroll_menu = self.master.add_scroll_menu(
            "Search results:", 0, 0, row_span=10, column_span=5, padx=1, pady=0
        )
        self.search_results_scroll_menu.add_text_color_rule(
            self.searched_string,
            BLACK_ON_GREEN,
            "contains",
            match_type="regex",
        )
        self.search_results_scroll_menu.add_key_command(
            keys.KEY_ENTER,
            self.display_selected_block,
        )

        self.result_content_box = self.master.add_text_block(
            "Block content:", 0, 5, row_span=9, column_span=5, padx=1, pady=0
        )
        self.result_content_box.add_key_command(
            keys.KEY_F5,
            self.open_save_popup,
        )
        self.result_content_box.add_key_command(
            keys.KEY_F6,
            self.display_previous_block,
        )
        self.result_content_box.add_key_command(
            keys.KEY_F7,
            self.display_next_block,
        )

        self.previous_button = self.master.add_button(
            "<",
            9,
            5,
            row_span=1,
            column_span=1,
            padx=1,
            pady=0,
            command=self.display_previous_block,
        )
        self.previous_button.set_color(1)

        self.next_button = self.master.add_button(
            ">",
            9,
            8,
            row_span=1,
            column_span=1,
            padx=1,
            pady=0,
            command=self.display_next_block,
        )
        self.next_button.set_color(1)

        self.save_file_button = self.master.add_button(
            "Save Block",
            9,
            6,
            row_span=1,
            column_span=2,
            padx=1,
            pady=0,
            command=self.open_save_popup,
        )
        self.save_file_button.set_color(4)

        self.exit_button = self.master.add_button(
            "Exit",
            9,
            9,
            row_span=1,
            column_span=1,
            padx=1,
            pady=0,
            command=self.master.stop,
        )
        self.exit_button.set_color(3)

    def populate_result_list(self):
        """Poll grep output and populate result list."""
        while True:
            try:
                new_results, self.result_index = search.yield_new_results(
                    self.queue_object,
                    self.result_index,
                )
            except TypeError:
                # If no new results
                sleep(1)
                continue

            self.add_results_to_list(new_results=new_results)
            self.set_title()

            # Sleeps to avoid unnecessary overload
            sleep(1)

    def add_results_to_list(self, new_results: list):
        """Add new results from the grep command to the left hand result list.

        Args:
            new_results (list): New results from the grep command.
        """
        for result in new_results:
            string_result = str(result)[2:-1]
            inode = findall(r"^([0-9]+)\:", string_result)[0]
            content = string_result[len(inode) + 1 :]
            self.inodes.append(int(inode))
            self.search_results_scroll_menu.add_item(content)

    def update_block_number(self):
        """Update currently screened block number upon user selection."""
        inode = self.inodes[
            int(self.search_results_scroll_menu.get_selected_item_index())
        ]
        self.current_block = str(int(inode / self.block_size))
        LOGGER.write("debug", f"Displayed block set to {self.current_block}")

    def display_selected_block(self):
        """Bundle updating + displaying block.

        Called when the user select a result in the left hand list.
        """
        self.update_block_number()
        self.display_block(self.current_block)

    def open_save_popup(self):
        """Open a popup displaying save options."""
        if self.current_block is None:
            self.master.show_message_popup(
                "",
                "Please select a block first.",
            )
            return

        screen_choices = [
            "Save currently displayed block",
            "Explore neighboring blocks and save it all",
            "Cancel",
        ]
        self.master.show_menu_popup(
            "How do you want to save it ?",
            screen_choices,
            self.handle_save_popup_choice,
        )

    def handle_save_popup_choice(self, choice: str):
        """Launch the action selected by the user (save, explore, exit).

        Args:
            choice (str): User choice given by open_save_popup function.
        """
        if choice == "Explore neighboring blocks and save it all":
            handler.SCREENS_HANDLER.open_screen(
                "screen",
                partition=self.partition,
                block=self.current_block,
            )
        elif choice == "Save currently displayed block":
            SAVER.save_result(
                current_block=self.current_block,
                result=self.current_result,
            )
            self.master.show_message_popup("", "Result saved.")
