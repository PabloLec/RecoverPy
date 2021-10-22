from time import sleep


def test_grep(TEST_SEARCH_VIEW):
    sleep(1)
    results = TEST_SEARCH_VIEW.search_results_scroll_menu.get_item_list()

    assert len(results) == 1


def test_dd(TEST_SEARCH_VIEW):
    TEST_SEARCH_VIEW.search_results_scroll_menu.set_selected_item_index(0)
    TEST_SEARCH_VIEW.display_selected_block()

    text = TEST_SEARCH_VIEW.result_content_box.get()

    assert "TEST STRING" in text


def test_previous_block(TEST_SEARCH_VIEW):
    TEST_SEARCH_VIEW.display_previous_block()

    text = TEST_SEARCH_VIEW.result_content_box.get()

    assert "TEST STRING" not in text
    assert "Integer vitae" in text


def test_next_block(TEST_SEARCH_VIEW):
    TEST_SEARCH_VIEW.display_next_block()

    text = TEST_SEARCH_VIEW.result_content_box.get()

    assert "TEST STRING" in text
