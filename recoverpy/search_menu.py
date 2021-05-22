from subprocess import PIPE, DEVNULL, Popen, check_output, call
from threading import Thread
from queue import Queue
from shlex import quote

import io
import time
import re
import py_cui

from recoverpy import window_handler as WINDOW_HANDLER
from recoverpy import saver as SAVER
from recoverpy import logger as LOGGER
from recoverpy import menu_with_block_display as BLOCK_DISPLAY_MENU


class SearchMenu(BLOCK_DISPLAY_MENU.MenuWithBlockDisplay):
    """Search menu is displayed after Parameters menu.
    On the left hand scroll menu, results from the grep command will be listed.
    On the right hand textbox, result of a dd command will be displayed when the user
    selects a block.

    Args:
        BLOCK_DISPLAY_MENU (MenuWithBlockDisplay: Composition to inherit block display
        methods.

    Attributes:
        master (py_cui.PyCUI): PyCUI constructor.
        queue_object (Queue): Queue object where grep command stdout will be stored.
        result_index (int): Number of results already processed.
        grep_progress (str): Formated output of 'progress' command.
        partition (str): System partition selected by user for search.
        block_size (int): Size of partition block for dd parsing.
        searched_string (str): String given by the user that will be searched by dd command.
    """

    def __init__(self, master: py_cui.PyCUI, partition: str, string_to_search: str):
        """Constructor for Search menu

        Args:
            master (py_cui.PyCUI): PyCUI constructor
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

        LOGGER.write("info", "Starting 'SearchMenu' CUI window")

        self.create_ui_content()

        self.start_search()

        LOGGER.write(
            "info",
            f"Raw searched string:\n{self.searched_string}",
        )
        LOGGER.write(
            "info",
            f"Formated searched string:\n{quote(self.searched_string)}",
        )

    def set_title(self):
        if self.grep_progress != "":
            title = f"{self.grep_progress} - {str(self.result_index)} results"
        else:
            title = f"{str(self.result_index)} results"

        self.master.set_title(title)

    def create_ui_content(self):
        """Handles the creation of the UI elements."""

        self.search_results_cell = self.master.add_scroll_menu(
            "Search results:", 0, 0, row_span=10, column_span=5, padx=1, pady=0
        )
        self.search_results_cell.add_key_command(py_cui.keys.KEY_ENTER, self.display_selected_block)

        self.result_content_box = self.master.add_text_block(
            "Block content:", 0, 5, row_span=9, column_span=5, padx=1, pady=0
        )
        self.result_content_box.add_key_command(py_cui.keys.KEY_F5, self.open_save_menu)
        self.result_content_box.add_key_command(py_cui.keys.KEY_F6, self.display_previous_block)
        self.result_content_box.add_key_command(py_cui.keys.KEY_F7, self.display_next_block)

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
            command=self.open_save_menu,
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

    def is_progress_installed(self):
        """Verifies if 'progress' tool is installed on current system.

        Returns:
            bool: 'progress' is installed.
        """

        output = call("command -v progress", shell=True)
        if output == 0:
            return True
        else:
            return False

    def monitor_progress(self, grep_pid: int):
        """Uses 'progress' tool to monitor grep advancement.

        Args:
            grep_pid (int): PID of grep process.
        """
        while True:
            output = check_output(["progress", "-p", str(grep_pid)], stderr=DEVNULL).decode("utf8")

            try:
                progress = re.findall(r"([0-9]+\.[0-9]+\%[^\)]+\))", output)[0]
            except IndexError:
                continue

            self.grep_progress = progress
            LOGGER.write("debug", f"Progress: {progress}")
            self.set_title()
            time.sleep(1)

    def start_search(self):
        """Function is called within __init__
        Launches:
        - Process executing the grep command.
        - If available, thread using 'progress' tool to monitor grep.
        - Thread to store the grep output in a queue object.
        - Thread to populate the result box dynamically.
        """

        grep_process = Popen(
            ["grep", "-a", "-b", self.searched_string, self.partition],
            stdin=None,
            stdout=PIPE,
            stderr=None,
        )

        if self.is_progress_installed():
            monitor_progress_thread = Thread(target=self.monitor_progress, args=(grep_process.pid,))
            monitor_progress_thread.daemon = True
            monitor_progress_thread.start()

        enqueue_grep_output_thread = Thread(
            target=self.enqueue_grep_output,
            args=(grep_process.stdout, self.queue_object),
        )
        enqueue_grep_output_thread.daemon = True
        enqueue_grep_output_thread.start()

        LOGGER.write("debug", "Started searching thread")

        yield_results_thread = Thread(target=self.populate_result_list)
        yield_results_thread.daemon = True
        yield_results_thread.start()

        LOGGER.write("debug", "Started output fetching thread")

    def enqueue_grep_output(self, out: io.BufferedReader, queue: Queue):
        """Function called in a thread to store the grep command output in
        a queue object.

        Args:
            out (io.BufferedReader): Output of grep process
            queue (Queue): Queue object to store stdout
        """

        for line in iter(out.readline, b""):
            queue.put(line)
        out.close()

    def yield_new_results(self):
        """Probes the queue object for new results.
        If any, returns it to populate the result box.

        Returns:
            List[str]: List of new results
        """

        new_results = []

        # Returns if no new result
        if len(list(self.queue_object.queue)) == self.result_index:
            return []

        queue_list = list(self.queue_object.queue)

        for queue_element in queue_list[self.result_index :]:
            new_results.append(queue_element)

        self.result_index = len(queue_list)

        return new_results

    def populate_result_list(self):
        """Dynamically populates the left hand result list with new results from the
        grep command"""

        while True:
            new_results = self.yield_new_results()
            for result in new_results:
                string_result = str(result)[2:-1]

                LOGGER.write("debug", "New result found: " + string_result[:30] + " ...")

                self.search_results_cell.add_item(string_result)
            self.set_title()

            # Sleeps to avoid unnecessary overload
            # This should not affect Popen's GIL
            time.sleep(1)

    def update_block_number(self):
        """Updates currently viewed block number when the user selects one in the list."""

        item_index = self.search_results_cell.get_selected_item_index()
        item_list = self.search_results_cell.get_item_list()

        item = item_list[item_index]
        inode = int(re.findall(r"^([0-9]+)\:", item)[0])
        self.current_block = str(int(inode / self.block_size))

        LOGGER.write(
            "debug",
            f"Displayed block set to {str(self.current_block)}",
        )

    def display_selected_block(self):
        """Function called when the user select a result in the left hand list.
        Bundles updating + displaying block.
        """

        self.update_block_number()
        self.display_block(self.current_block)

    def open_save_menu(self):
        """Opens a menu displaying save options."""

        menu_choices = [
            "Save currently displayed block",
            "Explore neighboring blocks and save it all",
            "Cancel",
        ]
        self.master.show_menu_popup("How do you want to save it ?", menu_choices, self.handle_save_menu_choice)

    def handle_save_menu_choice(self, choice: str):
        """Depending on user choice, function will either directly save the output in
        a text file, open a more detailed menu called BlockMenu or just exit.

        Args:
            choice (str): User choice given by open_save_menu function.
        """

        if choice == "Save currently displayed block":
            SAVER.save_result(current_block=self.current_block, result=self.current_result)

            self.master.show_message_popup("", "Result saved.")
        elif choice == "Explore neighboring blocks and save it all":
            WINDOW_HANDLER.open_block_menu(partition=self.partition, block=self.current_block)
        elif choice == "Cancel":
            pass
