from time import sleep

from py_cui import PyCUI

import recoverpy


def test_block_ui(TEST_FILE):
    search_view = recoverpy.views.view_search.SearchView(
        master=PyCUI(10, 10),
        partition=TEST_FILE,
        string_to_search="TEST STRING",
    )
    sleep(2)
    print(search_view.search_results_scroll_menu.get_item_list())

    assert False
