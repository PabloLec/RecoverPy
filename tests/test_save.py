import pathlib
from time import sleep

from py_cui import keys

import recoverpy


def test_save_single_block(SEARCH_SCREEN):
    sleep(1.5)
    SEARCH_SCREEN.search_results_scroll_menu._handle_key_press(keys.KEY_ENTER)
    SEARCH_SCREEN.handle_save_popup_choice(choice="Save currently displayed block")

    saved_file = recoverpy.utils.saver.SAVER.last_saved_file
    content = pathlib.Path(saved_file).read_text()

    expected = "TEST OUTPUT"

    assert content == expected


def test_save_multiple_blocks(BLOCK_SCREEN):
    for i in range(3):
        BLOCK_SCREEN.current_block = str(i)
        BLOCK_SCREEN.current_result = f"TEST {i}"
        BLOCK_SCREEN.add_block_to_file()

    BLOCK_SCREEN.save_file()

    saved_file = recoverpy.utils.saver.SAVER.last_saved_file
    content = pathlib.Path(saved_file).read_text()

    expected = "TEST 0\nTEST 1\nTEST 2"

    assert content == expected
