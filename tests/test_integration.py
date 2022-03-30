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


def test_wrong_save_path():
    assert get_screen().master._popup is None

    save_path_textbox = get_screen().master.get_widgets()[0]
    save_path_textbox._handle_key_press(keys.KEY_T_LOWER)
    save_path_confirm_button = get_screen().master.get_widgets()[1]
    save_path_confirm_button._handle_key_press(keys.KEY_ENTER)
    assert get_screen().master._popup is not None

    get_screen().master._popup._handle_key_press(keys.KEY_ENTER)
    assert get_screen().master._popup is None


def test_wrong_log_path():
    assert get_screen().master._popup is None

    log_path_textbox = get_screen().master.get_widgets()[2]
    log_path_textbox._handle_key_press(keys.KEY_T_LOWER)
    log_path_confirm_button = get_screen().master.get_widgets()[3]
    log_path_confirm_button._handle_key_press(keys.KEY_ENTER)
    assert get_screen().master._popup is not None

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

    save_button = get_screen().master.get_widgets()[7]
    save_button._handle_key_press(keys.KEY_ENTER)

    recoverpy.ui.handler.SCREENS_HANDLER.open_screen("parameters")


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
