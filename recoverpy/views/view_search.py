from time import sleep
from queue import Queue
from shlex import quote
from re import findall
import py_cui

from recoverpy import views_handler as _VIEWS_HANDLER
from recoverpy.views import menu_with_block_display as _BLOCK_DISPLAY_MENU
from recoverpy.saver import SAVER as _SAVER
from recoverpy import search_functions as _SEARCH
from recoverpy.logger import LOGGER as _LOGGER


class SearchView(_BLOCK_DISPLAY_MENU.MenuWithBlockDisplay):
    """SearchView is displayed after Parameters view.
    On the left hand scroll view, results from the grep command will be listed.
    On the right hand textbox, result of a dd command will be displayed when the user
    selects a block.

    Args:
        _BLOCK_DISPLAY_MENU (MenuWithBlockDisplay: Composition to inherit block display
        methods.

    Attributes:
        master (py_cui.PyCUI): PyCUI main object for UI.
        queue_object (Queue): Queue object where grep command stdout will be stored.
        result_index (int): Number of results already processed.
        grep_progress (str): Formated output of 'progress' command.
        partition (str): System partition selected by user for search.
        block_size (int): Size of partition block for dd parsing.
        searched_string (str): String given by the user that will be searched by dd command.
    """

    def __init__(self, master: py_cui.PyCUI, partition: str, string_to_search: str):
        """Constructor SearchView

        Args:
            master (py_cui.PyCUI): PyCUI main object for UI.
            partition (str): System partition to search
        """

        super().__init__()

        self.master = master
        self.master.set_refresh_timeout(1)

        self.queue_object = Queue()
        self.result_index = 0

        self.grep_progress = ""

        self.partition = partition
        self.block_size = 512

        self.searched_string = string_to_search

        _LOGGER.write("info", "Starting 'SearchView' CUI window")

        self.create_ui_content()

        _SEARCH.start_search(self)

        _LOGGER.write(
            "info",
            f"Raw searched string:\n{self.searched_string}",
        )
        _LOGGER.write(
            "info",
            f"Formated searched string:\n{quote(self.searched_string)}",
        )

    def set_title(self):
        """Set window title based on number of results and search progress."""

        if self.grep_progress != "":
            title = f"{self.grep_progress} - {str(self.result_index)} results"
        else:
            title = f"{str(self.result_index)} results"

        self.master.set_title(title)

    def create_ui_content(self):
        """Handle the creation of the UI elements."""

        self.search_results_scroll_menu = self.master.add_scroll_menu(
            "Search results:", 0, 0, row_span=10, column_span=5, padx=1, pady=0
        )
        self.search_results_scroll_menu.add_key_command(
            py_cui.keys.KEY_ENTER,
            self.display_selected_block,
        )

        self.result_content_box = self.master.add_text_block(
            "Block content:", 0, 5, row_span=9, column_span=5, padx=1, pady=0
        )
        self.result_content_box.add_key_command(
            py_cui.keys.KEY_F5,
            self.open_save_popup,
        )
        self.result_content_box.add_key_command(
            py_cui.keys.KEY_F6,
            self.display_previous_block,
        )
        self.result_content_box.add_key_command(
            py_cui.keys.KEY_F7,
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

    def populate_result_list(self):
        """Poll grep output and populate result list."""

        while True:
            try:
                new_results, self.result_index = _SEARCH.yield_new_results(
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
            self.search_results_scroll_menu.add_item(string_result)

            _LOGGER.write("debug", "New result found: " + string_result[:30] + " ...")

    def update_block_number(self):
        """Update currently viewed block number when the user selects one in the list."""

        item = self.search_results_scroll_menu.get()
        inode = int(findall(r"^([0-9]+)\:", item)[0])
        self.current_block = str(int(inode / self.block_size))

        _LOGGER.write(
            "debug",
            f"Displayed block set to {str(self.current_block)}",
        )

    def display_selected_block(self):
        """FCalled when the user select a result in the left hand list.
        Bundles updating + displaying block.
        """

        self.update_block_number()
        self.display_block(self.current_block)

    def open_save_popup(self):
        """Open a popup displaying save options."""

        view_choices = [
            "Save currently displayed block",
            "Explore neighboring blocks and save it all",
            "Cancel",
        ]
        self.master.show_menu_popup(
            "How do you want to save it ?",
            view_choices,
            self.handle_save_popup_choice,
        )

    def handle_save_popup_choice(self, choice: str):
        """Depending on user choice, method will either directly save the output in
        a text file, open a more detailed view called ResultsView or just exit.

        Args:
            choice (str): User choice given by open_save_popup function.
        """

        if choice == "Save currently displayed block":
            _SAVER.save_result(
                current_block=self.current_block,
                result=self.current_result,
            )
            self.master.show_message_popup("", "Result saved.")
        elif choice == "Explore neighboring blocks and save it all":
            _VIEWS_HANDLER.VIEWS_HANDLER.open_view_results(
                partition=self.partition,
                block=self.current_block,
            )
