from py_cui import GREEN_ON_BLACK, YELLOW_ON_BLACK, keys

from recoverpy.ui import handler
from recoverpy.ui.widgets.screen_type import ScreenType


def set_content(screen):
    screen.partitions_list_scroll_menu = screen.master.add_scroll_menu(
        "Select a partition to search:", 0, 0, row_span=9, column_span=5
    )
    screen.partitions_list_scroll_menu.add_key_command(
        keys.KEY_ENTER, screen.select_partition
    )
    screen.partitions_list_scroll_menu.add_text_color_rule(
        "Mounted at",
        YELLOW_ON_BLACK,
        "contains",
    )
    screen.partitions_list_scroll_menu.set_selected_color(GREEN_ON_BLACK)

    screen.string_text_box = screen.master.add_text_block(
        "Enter a text to search:",
        0,
        5,
        row_span=9,
        column_span=5,
    )

    screen.confirm_search_button = screen.master.add_button(
        "Start",
        9,
        4,
        row_span=1,
        column_span=2,
        padx=0,
        pady=0,
        command=screen.confirm_search,
    )
    screen.confirm_search_button.set_color(4)

    screen.open_config_button = screen.master.add_button(
        "Settings",
        9,
        8,
        row_span=1,
        column_span=2,
        padx=1,
        pady=0,
        command=lambda: handler.SCREENS_HANDLER.open_screen(ScreenType.CONFIG),
    )
    screen.open_config_button.set_color(1)
