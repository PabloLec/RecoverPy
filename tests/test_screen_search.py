import pathlib
from time import sleep

from py_cui import keys

import recoverpy


def test_search_ui(SEARCH_SCREEN):
    instance_dir = dir(SEARCH_SCREEN)

    assert "search_results_scroll_menu" in instance_dir
    assert "blockcontent_box" in instance_dir
    assert "previous_button" in instance_dir
    assert "next_button" in instance_dir
    assert "save_file_button" in instance_dir
    assert "exit_button" in instance_dir


def test_blocklist_population(SEARCH_SCREEN):
    sleep(1.5)
    item_list = SEARCH_SCREEN.search_results_scroll_menu.get_item_list()
    expected = [
        " Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod\\n",
        " Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod\\n",
        " Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod\\n",
    ]
    assert item_list == expected


def test_search_title(SEARCH_SCREEN):
    assert SEARCH_SCREEN.master._title == "100% - Search completed - 3 results"


def test_block_number_update(SEARCH_SCREEN):
    SEARCH_SCREEN.search_results_scroll_menu._handle_key_press(keys.KEY_UP_ARROW)
    SEARCH_SCREEN.search_results_scroll_menu._handle_key_press(keys.KEY_ENTER)
    item = " Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod\\n"

    assert SEARCH_SCREEN.current_block == "1"
    assert SEARCH_SCREEN.search_results_scroll_menu.get() == item


def test_save_search_result(SEARCH_SCREEN, tmp_path):
    recoverpy.utils.saver.SAVER.save_path = tmp_path

    SEARCH_SCREEN.handle_save_popup_choice(choice="Save currently displayed block")

    saved_file = recoverpy.utils.saver.SAVER.last_saved_file

    content = pathlib.Path(saved_file).read_text()
    expected = "TEST OUTPUT"

    assert content == expected
