from os import environ

from py_cui import keys
from pytest import mark

from recoverpy.lib.helper import is_dependency_installed


def test_search_ui(SEARCH_SCREEN):
    instance_dir = dir(SEARCH_SCREEN)

    assert "search_results_scroll_menu" in instance_dir
    assert "block_content_box" in instance_dir
    assert "previous_button" in instance_dir
    assert "next_button" in instance_dir
    assert "save_file_button" in instance_dir
    assert "exit_button" in instance_dir


def test_blocklist_population(SEARCH_SCREEN):
    item_list = SEARCH_SCREEN.search_results_scroll_menu.get_item_list()
    expected = [
        " Lorem ipsum dolor sit amet, test consectetur adipiscing elit, sed do ",
        " Lorem ipsum dolor sit amet, test consectetur adipiscing elit, sed da ",
        " Lorem ipsum dolor sit amet, test consectetur adipiscing elit, sed du ",
    ]
    assert item_list == expected


@mark.skipif(
    environ.get("IS_GITHUB_RUNNER") == "true",
    reason="Privileges issues with GitHub Actions",
)
def test_search_title(SEARCH_SCREEN):
    if is_dependency_installed("progress"):
        assert SEARCH_SCREEN.master._title == "100% - Search completed - 3 results"
    else:
        assert SEARCH_SCREEN.master._title == "3 results"


def test_block_number_update(SEARCH_SCREEN):
    SEARCH_SCREEN.search_results_scroll_menu._handle_key_press(keys.KEY_UP_ARROW)
    SEARCH_SCREEN.search_results_scroll_menu._handle_key_press(keys.KEY_ENTER)
    item = " Lorem ipsum dolor sit amet, test consectetur adipiscing elit, sed do "

    assert SEARCH_SCREEN.current_block == "0"
    assert SEARCH_SCREEN.search_results_scroll_menu.get() == item


def test_grep_length(SEARCH_SCREEN):
    results = SEARCH_SCREEN.search_results_scroll_menu.get_item_list()

    assert len(results) == 3


def test_dd(SEARCH_SCREEN):
    SEARCH_SCREEN.search_results_scroll_menu.set_selected_item_index(0)
    SEARCH_SCREEN.display_selected_block()

    text = SEARCH_SCREEN.block_content_box.get()

    assert "TEST OUTPUT" in text


def test_previous_block(SEARCH_SCREEN):
    SEARCH_SCREEN.display_previous_block()

    assert SEARCH_SCREEN.current_block == "0"


def test_next_block(SEARCH_SCREEN):
    SEARCH_SCREEN.display_next_block()

    assert SEARCH_SCREEN.current_block == "1"
