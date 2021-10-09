from py_cui import PyCUI


class ConfigView:
    def __init__(self, master: PyCUI):
        self.master = master
        self.create_ui_content()

    def create_ui_content(self):
        """Handle the creation of the UI elements."""
        self.master.add_label(
            self, "Save Path", 1, 1, row_span=1, column_span=1, padx=1, pady=0
        )
