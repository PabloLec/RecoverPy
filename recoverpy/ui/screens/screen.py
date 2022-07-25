from py_cui import PyCUI

from recoverpy.ui import widgets


class Screen:
    def __init__(self, master: PyCUI):
        self.master = master
        self.master.set_refresh_timeout(1)

    def create_ui_content(self):
        widgets.init_ui(self)
