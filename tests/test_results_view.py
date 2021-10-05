import recoverpy


def test_block_ui(RESULTS_VIEW):
    RESULTS_VIEW.create_ui_content()
    instance_dir = dir(RESULTS_VIEW)

    assert "previous_button" in instance_dir
    assert "next_button" in instance_dir
    assert "result_content_box" in instance_dir
    assert "add_result_button" in instance_dir
    assert "save_file_button" in instance_dir
    assert "go_back_button" in instance_dir


def test_add_block_to_file(RESULTS_VIEW):
    RESULTS_VIEW.create_ui_content()

    for i in range(0, 3):
        RESULTS_VIEW.current_block = str(i)
        RESULTS_VIEW.current_result = f"TEST {i}"
        RESULTS_VIEW.add_block_to_file()

    expected = {"0": "TEST 0", "1": "TEST 1", "2": "TEST 2"}

    assert RESULTS_VIEW.saved_blocks_dict == expected


def test_save_multiple_blocks(RESULTS_VIEW, tmp_path):
    recoverpy.utils.saver._save_path = tmp_path

    for i in range(0, 3):
        RESULTS_VIEW.current_block = str(i)
        RESULTS_VIEW.current_result = f"TEST {i}"
        RESULTS_VIEW.add_block_to_file()

    RESULTS_VIEW.save_file()

    saved_file = recoverpy.utils.saver.SAVER.last_saved_file

    with open(saved_file) as f:
        content = f.read()

    expected = "TEST 0\nTEST 1\nTEST 2\n"

    assert content == expected
