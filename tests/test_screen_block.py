def test_block_ui(BLOCK_SCREEN):
    instance_dir = dir(BLOCK_SCREEN)

    assert "previous_button" in instance_dir
    assert "next_button" in instance_dir
    assert "block_content_box" in instance_dir
    assert "add_blockbutton" in instance_dir
    assert "save_file_button" in instance_dir
    assert "go_back_button" in instance_dir


def test_add_block_to_file(BLOCK_SCREEN):
    for i in range(3):
        BLOCK_SCREEN.current_block = str(i)
        BLOCK_SCREEN.current_result = f"TEST {i}"
        BLOCK_SCREEN.add_block_to_file()

    expected = {"0": "TEST 0", "1": "TEST 1", "2": "TEST 2"}

    assert BLOCK_SCREEN.saved_blocks_dict == expected
