from os import environ

from py_cui import keys

import recoverpy


def get_screen():
    return recoverpy.ui.handler.SCREENS_HANDLER.screens[
        recoverpy.ui.handler.SCREENS_HANDLER.current_screen
    ]


def test_main(mock_config):
    recoverpy.main()

    assert recoverpy.ui.handler.SCREENS_HANDLER.current_screen == "parameters"
    assert environ["TERM"] == "xterm-256color"
    assert recoverpy.utils.saver.SAVER.save_path == mock_config
    assert recoverpy.utils.logger.LOGGER.log_path == mock_config
    assert recoverpy.utils.logger.LOGGER.log_enabled is True


def test_open_config_screen():
    get_screen().open_config_button._handle_key_press(keys.KEY_ENTER)
    assert "ConfigScreen" in str(type(get_screen()))


def test_wrong_save_path_confirm():
    assert get_screen().master._popup is None

    save_path_textbox = get_screen().master.get_widgets()[0]
    save_path_textbox._handle_key_press(keys.KEY_T_LOWER)
    save_path_confirm_button = get_screen().master.get_widgets()[1]
    save_path_confirm_button._handle_key_press(keys.KEY_ENTER)
    assert get_screen().master._popup is not None
    assert get_screen().master._popup.get_title() == "Path invalid"

    get_screen().master._popup._handle_key_press(keys.KEY_ENTER)
    assert get_screen().master._popup is None


def test_wrong_save_path_save_all():
    save_button = get_screen().master.get_widgets()[7]
    save_button._handle_key_press(keys.KEY_ENTER)

    assert get_screen().master._popup is not None
    assert get_screen().master._popup.get_title() == "Path invalid"

    get_screen().master._popup._handle_key_press(keys.KEY_ENTER)
    assert get_screen().master._popup is None


def test_correct_save_path_confirm():
    save_path_textbox = get_screen().master.get_widgets()[0]
    save_path_textbox.set_text(str(recoverpy.utils.saver.SAVER.save_path))

    save_path_confirm_button = get_screen().master.get_widgets()[1]
    save_path_confirm_button._handle_key_press(keys.KEY_ENTER)

    assert get_screen().master._popup is not None
    assert get_screen().master._popup._text == "Save path changed successfully"

    get_screen().master._popup._handle_key_press(keys.KEY_ENTER)
    assert get_screen().master._popup is None


def test_wrong_log_path_confirm():
    assert get_screen().master._popup is None

    log_path_textbox = get_screen().master.get_widgets()[2]
    log_path_textbox._handle_key_press(keys.KEY_T_LOWER)
    log_path_confirm_button = get_screen().master.get_widgets()[3]
    log_path_confirm_button._handle_key_press(keys.KEY_ENTER)
    assert get_screen().master._popup is not None
    assert get_screen().master._popup.get_title() == "Path invalid"

    get_screen().master._popup._handle_key_press(keys.KEY_ENTER)
    assert get_screen().master._popup is None


def test_wrong_log_path_save_all():
    save_button = get_screen().master.get_widgets()[7]
    save_button._handle_key_press(keys.KEY_ENTER)

    assert get_screen().master._popup is not None
    assert get_screen().master._popup.get_title() == "Path invalid"

    get_screen().master._popup._handle_key_press(keys.KEY_ENTER)
    assert get_screen().master._popup is None


def test_correct_log_path_confirm():
    save_path_textbox = get_screen().master.get_widgets()[2]
    save_path_textbox.set_text(str(recoverpy.utils.logger.LOGGER.log_path))

    save_path_confirm_button = get_screen().master.get_widgets()[3]
    save_path_confirm_button._handle_key_press(keys.KEY_ENTER)

    assert get_screen().master._popup is not None
    assert get_screen().master._popup._text == "Log path changed successfully"

    get_screen().master._popup._handle_key_press(keys.KEY_ENTER)
    assert get_screen().master._popup is None


def test_set_logging():
    enable_logging_button = get_screen().master.get_widgets()[5]
    disable_logging_button = get_screen().master.get_widgets()[6]

    assert enable_logging_button.get_color() == 4
    assert disable_logging_button.get_color() == 1
    assert recoverpy.utils.logger.LOGGER.log_enabled is True

    disable_logging_button._handle_key_press(keys.KEY_ENTER)

    assert get_screen()._log_enabled is False

    assert enable_logging_button.get_color() == 1
    assert disable_logging_button.get_color() == 4
    assert recoverpy.utils.logger.LOGGER.log_enabled is True


def test_correct_config_save_all():
    save_button = get_screen().master.get_widgets()[7]
    save_button._handle_key_press(keys.KEY_ENTER)

    assert "ParametersScreen" in str(type(get_screen()))


def test_select_partition():
    get_screen().partitions_list_scroll_menu._handle_key_press(keys.KEY_DOWN_ARROW)
    selected_item = get_screen().partitions_list_scroll_menu.get()
    expected = "Name: sdb1  -  Type: ntfs  -  Mounted at: /media/disk2"

    assert selected_item == expected

    get_screen().partitions_list_scroll_menu._handle_key_press(keys.KEY_DOWN_ARROW)
    selected_item = get_screen().partitions_list_scroll_menu.get()
    expected = "Name: mmcblk0p1  -  Type: vfat"

    assert selected_item == expected

    get_screen().partitions_list_scroll_menu._handle_key_press(keys.KEY_ENTER)
    expected = "/dev/mmcblk0p1"

    assert get_screen().partition_to_search == expected


def test_type_searched_string():
    get_screen().string_text_box._handle_key_press(keys.KEY_T_LOWER)
    get_screen().string_text_box._handle_key_press(keys.KEY_E_LOWER)
    get_screen().string_text_box._handle_key_press(keys.KEY_S_LOWER)
    get_screen().string_text_box._handle_key_press(keys.KEY_T_LOWER)

    assert get_screen().string_text_box.get().strip() == "test"


def test_confirm_search():
    get_screen().confirm_search_button._handle_key_press(keys.KEY_ENTER)
    assert get_screen().master._popup is not None

    get_screen().master._popup._handle_key_press(keys.KEY_Y_LOWER)
    assert get_screen().master._popup is None
    assert "SearchScreen" in str(type(get_screen()))


def test_select_search_result():
    assert get_screen().blockcontent_box.get().strip() == ""

    get_screen().search_results_scroll_menu._handle_key_press(keys.KEY_DOWN_ARROW)
    get_screen().search_results_scroll_menu._handle_key_press(keys.KEY_ENTER)

    assert get_screen().blockcontent_box.get().strip() == "TEST OUTPUT"


def test_open_save_popup():
    save_button = get_screen().master.get_widgets()[4]
    save_button._handle_key_press(keys.KEY_ENTER)

    assert get_screen().master._popup is not None

    expected_item_list = [
        "Save currently displayed block",
        "Explore neighboring blocks and save it all",
        "Cancel",
    ]

    assert get_screen().master._popup.get_item_list() == expected_item_list


def test_save_displayed_block():
    get_screen().master._popup.set_selected_item_index(0)
    get_screen().master._popup._handle_key_press(keys.KEY_ENTER)

    saved_file_path = recoverpy.utils.saver.SAVER.last_saved_file
    with open(saved_file_path, "r") as f:
        assert f.read().strip() == "TEST OUTPUT"

    assert get_screen().master._popup is not None
    get_screen().master._popup._handle_key_press(keys.KEY_ENTER)


def test_go_to_block_screen():
    save_button = get_screen().master.get_widgets()[4]
    save_button._handle_key_press(keys.KEY_ENTER)

    get_screen().master._popup.set_selected_item_index(1)
    get_screen().master._popup._handle_key_press(keys.KEY_ENTER)
    assert "BlockScreen" in str(type(get_screen()))


def test_save_multiple_blocks():
    previous_button = get_screen().master.get_widgets()[0]
    block_textbox = get_screen().master.get_widgets()[2]
    add_block_button = get_screen().master.get_widgets()[3]
    save_file_button = get_screen().master.get_widgets()[4]

    assert block_textbox.get_title() == "Block 3"
    add_block_button._handle_key_press(keys.KEY_ENTER)
    previous_button._handle_key_press(keys.KEY_ENTER)

    assert block_textbox.get_title() == "Block 2"
    add_block_button._handle_key_press(keys.KEY_ENTER)
    previous_button._handle_key_press(keys.KEY_ENTER)

    assert block_textbox.get_title() == "Block 1"
    add_block_button._handle_key_press(keys.KEY_ENTER)
    add_block_button._handle_key_press(keys.KEY_ENTER)

    save_file_button._handle_key_press(keys.KEY_ENTER)
    saved_file_path = recoverpy.utils.saver.SAVER.last_saved_file
    with open(saved_file_path, "r") as f:
        assert f.read().strip() == "TEST OUTPUT\nTEST OUTPUT\nTEST OUTPUT"
