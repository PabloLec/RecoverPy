import recoverpy


def test_block_ui(RESULTS_SCREEN):
    RESULTS_SCREEN.create_ui_content()
    instance_dir = dir(RESULTS_SCREEN)

    assert "previous_button" in instance_dir
    assert "next_button" in instance_dir
    assert "blockcontent_box" in instance_dir
    assert "add_blockbutton" in instance_dir
    assert "save_file_button" in instance_dir
    assert "go_back_button" in instance_dir


def test_add_block_to_file(RESULTS_SCREEN):
    RESULTS_SCREEN.create_ui_content()

    for i in range(3):
        RESULTS_SCREEN.current_block = str(i)
        RESULTS_SCREEN.current_result = f"TEST {i}"
        RESULTS_SCREEN.add_block_to_file()

    expected = {"0": "TEST 0", "1": "TEST 1", "2": "TEST 2"}

    assert RESULTS_SCREEN.saved_blocks_dict == expected


def test_save_multiple_blocks(RESULTS_SCREEN, tmp_path):
    recoverpy.utils.saver._save_path = tmp_path

    for i in range(3):
        RESULTS_SCREEN.current_block = str(i)
        RESULTS_SCREEN.current_result = f"TEST {i}"
        RESULTS_SCREEN.add_block_to_file()

    RESULTS_SCREEN.save_file()

    saved_file = recoverpy.utils.saver.SAVER.last_saved_file

    with open(saved_file) as f:
        content = f.read()

    expected = "TEST 0\nTEST 1\nTEST 2\n"

    assert content == expected
