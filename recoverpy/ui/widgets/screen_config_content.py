from recoverpy.lib.logger import Logger
from recoverpy.lib.saver import Saver
from recoverpy.ui import handler


def set_content(screen):
    screen.save_path_box = screen.master.add_text_box(
        title="Save Path",
        row=0,
        column=1,
        row_span=1,
        column_span=8,
        padx=0,
        pady=0,
        initial_text=str(Saver().save_path),
    )

    screen.master.add_button(
        "Save",
        row=1,
        column=8,
        row_span=1,
        column_span=1,
        padx=0,
        pady=0,
        command=screen.set_save_path,
    ).set_color(1)

    screen.log_path_box = screen.master.add_text_box(
        title="Log Path",
        row=2,
        column=1,
        row_span=1,
        column_span=8,
        padx=0,
        pady=0,
        initial_text=str(Logger().log_path),
    )

    screen.master.add_button(
        "Save",
        row=3,
        column=8,
        row_span=1,
        column_span=1,
        padx=0,
        pady=0,
        command=screen.set_log_path,
    ).set_color(1)

    screen.master.add_label(
        title="Enable Logging",
        row=4,
        column=4,
        row_span=1,
        column_span=2,
        padx=0,
        pady=0,
    ).selectable = False

    screen.yes_button = screen.master.add_button(
        "Yes",
        row=5,
        column=3,
        row_span=1,
        column_span=1,
        padx=0,
        pady=0,
        command=screen.enable_logging,
    )

    screen.no_button = screen.master.add_button(
        "No",
        row=5,
        column=6,
        row_span=1,
        column_span=1,
        padx=0,
        pady=0,
        command=screen.disable_logging,
    )

    screen.master.add_button(
        "Save & Exit",
        row=8,
        column=2,
        row_span=1,
        column_span=2,
        padx=0,
        pady=0,
        command=screen.save_all,
    ).set_color(4)

    screen.master.add_button(
        "Cancel",
        row=8,
        column=6,
        row_span=1,
        column_span=2,
        padx=0,
        pady=0,
        command=handler.SCREENS_HANDLER.go_back,
    ).set_color(2)
