from typing import Optional

from textual.widgets import Label, ListItem

from recoverpy.lib.helper import get_inode, get_printable
from recoverpy.log.logger import log


class SearchResult:
    def __init__(self, line: str, inode: Optional[int] = None):
        self.inode = inode if inode is not None else get_inode(line)
        self.line = get_printable(line)
        self.list_item: Optional[ListItem] = None
        self.label: Optional[Label] = None
        self.css_class = "search-result"

    def create_list_item(self) -> None:
        try:
            self.label = Label(str(self.line), markup=False)
            self.list_item = ListItem(
                self.label,
                classes=self.css_class,
                id=f"search-result-{self.inode}",
            )
        except RuntimeError as e:
            log.error(f"search_result - Error creating list item: {e}")
            return
