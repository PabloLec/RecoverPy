from queue import Queue
from re import findall
from shlex import quote
from time import sleep

from py_cui import PyCUI

from recoverpy.ui import handler
from recoverpy.ui.screen_with_block_display import MenuWithBlockDisplay
from recoverpy.utils.helper import decode_printable, get_block_size
from recoverpy.utils.logger import LOGGER
from recoverpy.utils.saver import SAVER
from recoverpy.utils.search import SEARCH_ENGINE


class SearchScreen(MenuWithBlockDisplay):
    """Display search results and corresponding blocks content."""

    def __init__(self, master: PyCUI, partition: str, string_to_search: str):
        super().__init__(master)

        self.queue_object: Queue = Queue()
        self.blockindex: int = 0
        self.block_numbers: list = []
        self.partition: str = partition
        self.block_size: int = get_block_size(partition)
        self.searched_string: str = string_to_search
        self._encoded_search_string: bytes = string_to_search.encode()

        self.create_ui_content()

        SEARCH_ENGINE.start_search(self)
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

    def dequeue_results(self):
        while True:
            try:
                new_results: list
                new_results, self.blockindex = SEARCH_ENGINE.get_new_results(
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
            string_result: str = decode_printable(result)
            inode: str = findall(r"^([0-9]+)\:", string_result)[0]
            result_block_offset = self.find_result_block_offset(result)

            content_start: int = self.find_content_start(inode, string_result)
            content: str = string_result[content_start:]
            self.block_numbers.append(
                str(int(int(inode) / self.block_size) + result_block_offset)
            )
            self.search_results_scroll_menu.add_item(content)

    def find_result_block_offset(self, result: bytes) -> int:
        result_index: int = result.index(self._encoded_search_string)
        return int(result_index / self.block_size)

    def find_content_start(self, inode: str, result: str) -> int:
        searched_string_pos: int = result.index(self.searched_string)

        row_start_pos: int = self.search_results_scroll_menu.get_absolute_start_pos()[0]
        row_stop_pos: int = self.search_results_scroll_menu.get_absolute_stop_pos()[0]
        row_length = row_stop_pos - row_start_pos

        is_result_too_far: bool = (
            searched_string_pos + len(self.searched_string) > row_length
        )

        if is_result_too_far and len(result) - searched_string_pos > row_length:
            return searched_string_pos
        elif is_result_too_far:
            return len(result) - row_length
        else:
            return len(inode) + 1

    def update_block_number(self):
        self.current_block = self.block_numbers[
            int(self.search_results_scroll_menu.get_selected_item_index())
        ]

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
                "block",
                partition=self.partition,
                initial_block=self.current_block,
            )
        elif choice == "Save currently displayed block":
            SAVER.save_result_string(result=self.current_result)
            self.master.show_message_popup("", "Result saved.")
