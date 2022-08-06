from recoverpy.ui import handler


def set_content(screen):
    screen.previous_button = screen.master.add_button(
        "<",
        3,
        0,
        row_span=3,
        column_span=1,
        padx=1,
        pady=0,
        command=screen.display_previous_block,
    )
    screen.previous_button.set_color(1)

    screen.next_button = screen.master.add_button(
        ">",
        3,
        9,
        row_span=3,
        column_span=1,
        padx=1,
        pady=0,
        command=screen.display_next_block,
    )
    screen.next_button.set_color(1)

    screen.block_content_box = screen.master.add_text_block(
        "Block content:", 0, 1, row_span=9, column_span=8, padx=1, pady=0
    )
    screen.block_content_box.set_title(f"Block {screen.current_block}")

    screen.add_blockbutton = screen.master.add_button(
        "Add current block to file",
        9,
        0,
        row_span=1,
        column_span=5,
        padx=1,
        pady=0,
        command=screen.add_block_to_file,
    )
    screen.add_blockbutton.set_color(6)

    screen.save_file_button = screen.master.add_button(
        "Save file",
        9,
        5,
        row_span=1,
        column_span=3,
        padx=1,
        pady=0,
        command=screen.save_file,
    )
    screen.save_file_button.set_color(4)

    screen.go_back_button = screen.master.add_button(
        "Go back to previous screen",
        9,
        8,
        row_span=1,
        column_span=2,
        padx=1,
        pady=0,
        command=handler.SCREENS_HANDLER.go_back,
    )
    screen.go_back_button.set_color(2)
