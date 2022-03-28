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
    get_screen().start_search(is_confirmed=True)

    assert recoverpy.ui.handler.SCREENS_HANDLER.current_screen == "search"
