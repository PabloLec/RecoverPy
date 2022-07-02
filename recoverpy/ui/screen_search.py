from queue import Queue
from time import sleep

from py_cui import PyCUI

from recoverpy.ui import handler
from recoverpy.ui.screen_with_block_display import MenuWithBlockDisplay
from recoverpy.utils.helper import get_block_size, get_inode, get_printable
from recoverpy.utils.logger import LOGGER
from recoverpy.utils.saver import SAVER
from recoverpy.utils.search import Results, SearchEngine


class SearchScreen(MenuWithBlockDisplay):
    """Display search results and corresponding blocks content."""

    def __init__(self, master: PyCUI, partition: str, string_to_search: str):
        super().__init__(master)

        self.queue_object: Queue = Queue()
        self.block_index: int = 0
        self.block_numbers: list = []
        self.partition: str = partition
        self.block_size: int = get_block_size(partition)
        self.searched_string: str = string_to_search
        self._first_line: str = string_to_search.strip().splitlines()[0]
        self.search_engine: SearchEngine = SearchEngine()

        self.create_ui_content()
        self.search_engine.start_search(self)
        LOGGER.write("info", f"Raw searched string:\n{self.searched_string}")

    def set_title(self, grep_progress: str = None):
        title: str = (
            f"{grep_progress} - {self.block_index} results"
            if grep_progress
            else f"{self.block_index} results"
        )

        self.master.set_title(title)

        if "100%" in title:
            if self.block_index == 0:
                self.master.title_bar.set_color(22)
            else:
                self.master.title_bar.set_color(30)

    def dequeue_results(self):
        while True:
            results: Results = self.search_engine.get_new_results(
                self.queue_object, self.block_index
            )
            if results.is_empty():
                sleep(1)
                continue
            self.block_index = results.block_index

            self.add_results_to_list(new_results=results.lines)
            self.set_title()

            # Sleep to avoid unnecessary overload
            sleep(1)

    def add_results_to_list(self, new_results: list):
        for result in new_results:
            string_result: str = get_printable(result)
            inode: str = get_inode(string_result)
            result_block_offset = self.get_result_block_offset(string_result)

            real_result_block_start: int = (
                int(int(inode) / self.block_size) + result_block_offset
            )
            self.block_numbers.append(str(real_result_block_start))

            content_start: int = self.get_content_start(inode, string_result)
            content: str = string_result[content_start:]
            self.search_results_scroll_menu.add_item(content)

    def get_result_block_offset(self, result: str) -> int:
        result_index: int = result.find(self._first_line)
        return int(result_index / self.block_size)

    def get_content_start(self, inode: str, result: str) -> int:
        searched_string_pos: int = result.find(self._first_line)
        box_start_pos: int = self.search_results_scroll_menu.get_absolute_start_pos()[0]
        box_stop_pos: int = self.search_results_scroll_menu.get_absolute_stop_pos()[0]
        box_length: int = box_stop_pos - box_start_pos

        is_result_outside_box: bool = (
            searched_string_pos + len(self.searched_string) > box_length
        )
        is_result_longer_than_box: bool = len(result) - searched_string_pos > box_length

        if is_result_outside_box and is_result_longer_than_box:
            return searched_string_pos
        elif is_result_outside_box:
            return int(searched_string_pos - (box_length / 2))
        else:
            return len(inode) + 1

    def update_block_number(self):
        self.current_block = self.block_numbers[
            int(self.search_results_scroll_menu.get_selected_item_index())
        ]

    def fix_block_number(self):
        self.block_numbers[
            int(self.search_results_scroll_menu.get_selected_item_index())
        ] = self.search_engine.fix_block_number(self.current_block)
        self.update_block_number()

    def display_selected_block(self):
        self.update_block_number()
        self.fix_block_number()
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
