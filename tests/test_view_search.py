import recoverpy


def test_search_ui(SEARCH_SCREEN):
    SEARCH_SCREEN.create_ui_content()
    instance_dir = dir(SEARCH_SCREEN)

    assert "search_results_scroll_menu" in instance_dir
    assert "result_content_box" in instance_dir
    assert "previous_button" in instance_dir
    assert "next_button" in instance_dir
    assert "save_file_button" in instance_dir
    assert "exit_button" in instance_dir


def test_result_queue(SEARCH_SCREEN):
    (new_results, SEARCH_SCREEN.result_index,) = recoverpy.search.yield_new_results(
        queue_object=SEARCH_SCREEN.queue_object, result_index=SEARCH_SCREEN.result_index
    )

    lorem_results = [
        "- 1000: Lorem ipsum dolor sit amet, consectetur adipiscing elit, "
        "sed do eiusmod",
        "- 2000: Lorem ipsum dolor sit amet, consectetur adipiscing elit, "
        "sed do eiusmod",
        "- 3000: Lorem ipsum dolor sit amet, consectetur adipiscing elit, "
        "sed do eiusmod",
    ]
    assert new_results == lorem_results
    assert SEARCH_SCREEN.result_index == 3

    SEARCH_SCREEN.queue_object.put("TEST 1")
    (new_results, SEARCH_SCREEN.result_index,) = recoverpy.search.yield_new_results(
        queue_object=SEARCH_SCREEN.queue_object, result_index=SEARCH_SCREEN.result_index
    )

    assert new_results == ["TEST 1"]
    assert SEARCH_SCREEN.result_index == 4

    SEARCH_SCREEN.queue_object.put("TEST 2")
    SEARCH_SCREEN.queue_object.put("TEST 3")
    (new_results, SEARCH_SCREEN.result_index,) = recoverpy.search.yield_new_results(
        queue_object=SEARCH_SCREEN.queue_object, result_index=SEARCH_SCREEN.result_index
    )

    assert new_results == ["TEST 2", "TEST 3"]
    assert SEARCH_SCREEN.result_index == 6


def test_result_list_population(SEARCH_SCREEN):
    SEARCH_SCREEN.create_ui_content()

    (new_results, SEARCH_SCREEN.result_index,) = recoverpy.search.yield_new_results(
        queue_object=SEARCH_SCREEN.queue_object, result_index=SEARCH_SCREEN.result_index
    )
    SEARCH_SCREEN.add_results_to_list(new_results=new_results)

    item_list = SEARCH_SCREEN.search_results_scroll_menu.get_item_list()
    expected = [
        " Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmo",
        " Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmo",
        " Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmo",
    ]
    assert item_list == expected


def test_search_title(SEARCH_SCREEN):
    SEARCH_SCREEN.create_ui_content()

    (new_results, SEARCH_SCREEN.result_index,) = recoverpy.search.yield_new_results(
        queue_object=SEARCH_SCREEN.queue_object, result_index=SEARCH_SCREEN.result_index
    )
    SEARCH_SCREEN.set_title()

    assert SEARCH_SCREEN.master._title == "3 results"

    SEARCH_SCREEN.queue_object.put("TEST 1")
    (new_results, SEARCH_SCREEN.result_index,) = recoverpy.search.yield_new_results(
        queue_object=SEARCH_SCREEN.queue_object, result_index=SEARCH_SCREEN.result_index
    )
    SEARCH_SCREEN.grep_progress = "0.10% ( TEST )"
    SEARCH_SCREEN.set_title()

    assert SEARCH_SCREEN.master._title == "0.10% ( TEST ) - 4 results"


def test_block_number_update(SEARCH_SCREEN):
    SEARCH_SCREEN.create_ui_content()
    (new_results, SEARCH_SCREEN.result_index,) = recoverpy.search.yield_new_results(
        queue_object=SEARCH_SCREEN.queue_object, result_index=SEARCH_SCREEN.result_index
    )
    SEARCH_SCREEN.add_results_to_list(new_results=new_results)

    SEARCH_SCREEN.search_results_scroll_menu.set_selected_item_index(0)
    SEARCH_SCREEN.update_block_number()
    item_0 = " Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmo"

    assert SEARCH_SCREEN.current_block == "1"
    assert SEARCH_SCREEN.search_results_scroll_menu.get() == item_0

    SEARCH_SCREEN.search_results_scroll_menu.set_selected_item_index(2)
    SEARCH_SCREEN.update_block_number()
    item_2 = " Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmo"

    assert SEARCH_SCREEN.current_block == "4"
    assert SEARCH_SCREEN.search_results_scroll_menu.get() == item_2


def test_save_search_result(SEARCH_SCREEN, tmp_path):
    SEARCH_SCREEN.current_block = "NUM"
    SEARCH_SCREEN.current_result = "TEST CONTENT"
    recoverpy.utils.saver.SAVER.save_path = tmp_path

    SEARCH_SCREEN.handle_save_popup_choice(choice="Save currently displayed block")

    saved_file = recoverpy.utils.saver.SAVER.last_saved_file

    assert saved_file[-3:] == "NUM"

    with open(saved_file) as f:
        content = f.read()

    expected = "TEST CONTENT"

    assert content == expected
