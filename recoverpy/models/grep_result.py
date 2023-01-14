from typing import Optional
from asyncio import get_running_loop
from textual.widgets import Label, ListItem

from recoverpy.lib.helper import get_inode, get_printable


class GrepResult:
    def __init__(self, line: str):
        self.inode = get_inode(line)
        self.line = get_printable(line)
        self.list_item: Optional[ListItem] = None

    def create_list_item(self, css_class: str) -> None:
        try:
            get_running_loop()
        except RuntimeError:
            return

        self.list_item = ListItem(
            Label(str(self.line), markup=False), classes=css_class
        )
