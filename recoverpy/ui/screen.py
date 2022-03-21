from py_cui import PyCUI


class Screen:
    def __init__(self, master: PyCUI):
        self.master = master
        self.master.set_refresh_timeout(1)
