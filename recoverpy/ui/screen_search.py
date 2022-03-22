from queue import Queue
from re import findall
from shlex import quote
from time import sleep

from py_cui import BLACK_ON_GREEN, PyCUI, keys
from py_cui.widgets import ScrollMenu, ScrollTextBlock, Button

from recoverpy.utils import search
from recoverpy.ui import handler
from recoverpy.utils.logger import LOGGER
from recoverpy.utils.saver import SAVER
from recoverpy.ui.screen_with_block_display import MenuWithBlockDisplay


class SearchScreen(MenuWithBlockDisplay):
    """Display search results and corresponding blocks content."""

    block_size: int = 512

    def __init__(self, master: PyCUI, partition: str, string_to_search: str):
        """Initialize SearchScreen.

        Args:
            master (PyCUI): PyCUI main object for UI
            partition (str): System partition to search
            string_to_search (str): String to search in partition blocks
        """
        super().__init__(master)

        self.queue_object: Queue = Queue()
        self.blockindex: int = 0
        self.inodes: list = []
        self.partition: str = partition
        self.searched_string: str = string_to_search
        self.create_ui_content()

        search.start_search(self)

        LOGGER.write(
            "info",
            f"Raw searched string:\n{self.searched_string}\n"
            f"Formated searched string:\n{quote(self.searched_string)}",
        )

    def set_title(self, grep_progress: str = None):
        title: str = (
            f"{grep_progress} - {self.blockindex} results"
            if grep_progress
            else f"{self.blockindex} results"
        )

        self.master.set_title(title)

        if "100%" in title:
            if self.blockindex == 0:
                self.master.title_bar.set_color(22)
            else:
                self.master.title_bar.set_color(30)

    def create_ui_content(self):
        self.search_results_scroll_menu: ScrollMenu = self.master.add_scroll_menu(
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

        self.blockcontent_box: ScrollTextBlock = self.master.add_text_block(
            "Block content:", 0, 5, row_span=9, column_span=5, padx=1, pady=0
        )
        self.blockcontent_box.add_key_command(
            keys.KEY_F5,
            self.open_save_popup,
        )
        self.blockcontent_box.add_key_command(
            keys.KEY_F6,
            self.display_previous_block,
        )
        self.blockcontent_box.add_key_command(
            keys.KEY_F7,
            self.display_next_block,
        )

        self.previous_button: Button = self.master.add_button(
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

        self.next_button: Button = self.master.add_button(
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

        self.save_file_button: Button = self.master.add_button(
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

        self.exit_button: Button = self.master.add_button(
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

    def dequeue_results(self):
        while True:
            try:
                new_results: list
                new_results, self.blockindex = search.get_new_results(
                    self.queue_object,
                    self.blockindex,
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
        for result in new_results:
            string_result: str = str(result)[2:-1]
            inode: str = findall(r"^([0-9]+)\:", string_result)[0]
            content: str = string_result[len(inode) + 1 :]

            self.inodes.append(int(inode))
            self.search_results_scroll_menu.add_item(content)

    def update_block_number(self):
        inode: str = self.inodes[
            int(self.search_results_scroll_menu.get_selected_item_index())
        ]
        self.current_block = str(int(inode / self.block_size))

        LOGGER.write("debug", f"Displayed block set to {self.current_block}")

    def display_selected_block(self):
        self.update_block_number()
        self.display_block(self.current_block)

    def open_save_popup(self):
        if self.current_block is None:
            self.master.show_message_popup(
                "",
                "Please select a block first.",
            )
            return

        screen_choices: list = [
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
        if choice == "Explore neighboring blocks and save it all":
            handler.SCREENS_HANDLER.open_screen(
                "screen",
                partition=self.partition,
                block=self.current_block,
            )
        elif choice == "Save currently displayed block":
            SAVER.save_result_string(result=self.current_result)
            self.master.show_message_popup("", "Result saved.")
