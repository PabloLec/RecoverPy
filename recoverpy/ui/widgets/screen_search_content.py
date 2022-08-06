from py_cui import BLACK_ON_GREEN, keys


def set_content(screen):
    screen.search_results_scroll_menu = screen.master.add_scroll_menu(
        "Search results:", 0, 0, row_span=10, column_span=5, padx=1, pady=0
    )
    screen.search_results_scroll_menu.add_text_color_rule(
        screen.searched_string,
        BLACK_ON_GREEN,
        "contains",
        match_type="regex",
    )
    screen.search_results_scroll_menu.add_key_command(
        keys.KEY_ENTER,
        screen.display_selected_block,
    )

    screen.block_content_box = screen.master.add_text_block(
        "Block content:", 0, 5, row_span=9, column_span=5, padx=1, pady=0
    )
    screen.block_content_box.add_key_command(
        keys.KEY_F5,
        screen.open_save_popup,
    )
    screen.block_content_box.add_key_command(
        keys.KEY_F6,
        screen.display_previous_block,
    )
    screen.block_content_box.add_key_command(
        keys.KEY_F7,
        screen.display_next_block,
    )
    screen.block_content_box.add_text_color_rule(
        screen.searched_string,
        BLACK_ON_GREEN,
        "contains",
        match_type="regex",
    )

    screen.previous_button = screen.master.add_button(
        "<",
        9,
        5,
        row_span=1,
        column_span=1,
        padx=1,
        pady=0,
        command=screen.display_previous_block,
    )
    screen.previous_button.set_color(1)

    screen.next_button = screen.master.add_button(
        ">",
        9,
        8,
        row_span=1,
        column_span=1,
        padx=1,
        pady=0,
        command=screen.display_next_block,
    )
    screen.next_button.set_color(1)

    screen.save_file_button = screen.master.add_button(
        "Save Block",
        9,
        6,
        row_span=1,
        column_span=2,
        padx=1,
        pady=0,
        command=screen.open_save_popup,
    )
    screen.save_file_button.set_color(4)

    screen.exit_button = screen.master.add_button(
        "Exit",
        9,
        9,
        row_span=1,
        column_span=1,
        padx=1,
        pady=0,
        command=screen.master.stop,
    )
    screen.exit_button.set_color(3)
