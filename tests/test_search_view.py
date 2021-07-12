import recoverpy


def test_search_ui(_SEARCH_VIEW):
    _SEARCH_VIEW.create_ui_content()
    instance_dir = dir(_SEARCH_VIEW)

    assert "search_results_scroll_menu" in instance_dir
    assert "result_content_box" in instance_dir
    assert "previous_button" in instance_dir
    assert "next_button" in instance_dir
    assert "save_file_button" in instance_dir
    assert "exit_button" in instance_dir


def test_result_queue(_SEARCH_VIEW):
    new_results, _SEARCH_VIEW.result_index = recoverpy.search_functions.yield_new_results(
        queue_object=_SEARCH_VIEW.queue_object, result_index=_SEARCH_VIEW.result_index
    )

    lorem_results = [
        "- 1000: Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod",
        "- 2000: Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod",
        "- 3000: Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod",
    ]
    assert new_results == lorem_results
    assert _SEARCH_VIEW.result_index == 3

    _SEARCH_VIEW.queue_object.put("TEST 1")
    new_results, _SEARCH_VIEW.result_index = recoverpy.search_functions.yield_new_results(
        queue_object=_SEARCH_VIEW.queue_object, result_index=_SEARCH_VIEW.result_index
    )

    assert new_results == ["TEST 1"]
    assert _SEARCH_VIEW.result_index == 4

    _SEARCH_VIEW.queue_object.put("TEST 2")
    _SEARCH_VIEW.queue_object.put("TEST 3")
    new_results, _SEARCH_VIEW.result_index = recoverpy.search_functions.yield_new_results(
        queue_object=_SEARCH_VIEW.queue_object, result_index=_SEARCH_VIEW.result_index
    )

    assert new_results == ["TEST 2", "TEST 3"]
    assert _SEARCH_VIEW.result_index == 6


def test_result_list_population(_SEARCH_VIEW):
    _SEARCH_VIEW.create_ui_content()

    new_results, _SEARCH_VIEW.result_index = recoverpy.search_functions.yield_new_results(
        queue_object=_SEARCH_VIEW.queue_object, result_index=_SEARCH_VIEW.result_index
    )
    _SEARCH_VIEW.add_results_to_list(new_results=new_results)

    item_list = _SEARCH_VIEW.search_results_scroll_menu.get_item_list()
    expected = [
        "1000: Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmo",
        "2000: Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmo",
        "3000: Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmo",
    ]
    assert item_list == expected


def test_search_title(_SEARCH_VIEW):
    _SEARCH_VIEW.create_ui_content()

    new_results, _SEARCH_VIEW.result_index = recoverpy.search_functions.yield_new_results(
        queue_object=_SEARCH_VIEW.queue_object, result_index=_SEARCH_VIEW.result_index
    )
    _SEARCH_VIEW.set_title()

    assert _SEARCH_VIEW.master._title == "3 results"

    _SEARCH_VIEW.queue_object.put("TEST 1")
    new_results, _SEARCH_VIEW.result_index = recoverpy.search_functions.yield_new_results(
        queue_object=_SEARCH_VIEW.queue_object, result_index=_SEARCH_VIEW.result_index
    )
    _SEARCH_VIEW.grep_progress = "0.10% ( TEST )"
    _SEARCH_VIEW.set_title()

    assert _SEARCH_VIEW.master._title == "0.10% ( TEST ) - 4 results"


def test_block_number_update(_SEARCH_VIEW):
    _SEARCH_VIEW.create_ui_content()
    new_results, _SEARCH_VIEW.result_index = recoverpy.search_functions.yield_new_results(
        queue_object=_SEARCH_VIEW.queue_object, result_index=_SEARCH_VIEW.result_index
    )
    _SEARCH_VIEW.add_results_to_list(new_results=new_results)

    _SEARCH_VIEW.search_results_scroll_menu.set_selected_item_index(0)
    _SEARCH_VIEW.update_block_number()
    item_0 = "1000: Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmo"

    assert _SEARCH_VIEW.current_block == "1"
    assert _SEARCH_VIEW.search_results_scroll_menu.get() == item_0

    _SEARCH_VIEW.search_results_scroll_menu.set_selected_item_index(2)
    _SEARCH_VIEW.update_block_number()
    item_2 = "3000: Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmo"

    assert _SEARCH_VIEW.current_block == "5"
    assert _SEARCH_VIEW.search_results_scroll_menu.get() == item_2


def test_save_search_result(_SEARCH_VIEW, tmp_path):
    _SEARCH_VIEW.current_block = "NUM"
    _SEARCH_VIEW.current_result = "TEST CONTENT"
    recoverpy._SAVER._save_path = tmp_path

    _SEARCH_VIEW.handle_save_popup_choice(choice="Save currently displayed block")

    saved_file = recoverpy._SAVER.last_saved_file

    assert saved_file[-3:] == "NUM"

    with open(saved_file) as f:
        content = f.read()

    expected = "TEST CONTENT"

    assert content == expected
