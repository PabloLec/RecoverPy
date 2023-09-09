from typing import Optional

from textual.widgets import Label, ListItem

from recoverpy.lib.helper import get_inode, get_printable
from recoverpy.log.logger import log


class GrepResult:
    def __init__(self, line: str):
        self.inode = get_inode(line)
        self.line = get_printable(line)
        self.list_item: Optional[ListItem] = None

    def create_list_item(self, css_class: str) -> None:
        try:
            self.list_item = ListItem(
                Label(str(self.line), markup=False),
                classes=css_class,
                id=f"grep-result-{self.inode}",
            )
        except RuntimeError as e:
            log.error(f"grep_result - Error creating list item: {e}")
            return
