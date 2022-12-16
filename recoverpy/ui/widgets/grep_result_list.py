import asyncio
from random import randint

from textual.widgets import ListView, ListItem, Label

from lib.helper import get_printable


class GrepResultList(ListView):
    def __init__(self, *children, **kwargs):
        super().__init__(*children, **kwargs)
        self.results = []
        self.lock = asyncio.Lock()

    async def append(self, result: str) -> None:
        self.results.append(str(randint(0, 1000)))
        async with self.lock:
            await self._add_result_to_list()

    async def _add_result_to_list(self):
        while self._should_add_more():
            list_item = ListItem(Label(self.results[len(self.children)], markup=False))
            await super().append(list_item)

    async def on_mouse_scroll_down(self) -> None:
        async with self.lock:
            await self._add_result_to_list()

    def _get_list_index_to_show(self) -> int:
        size_with_overflow = self.size.height + int(self.scroll_y) + 10
        return size_with_overflow

    def _should_add_more(self) -> bool:
        is_at_bottom = len(self.children) >= len(self.results)
        is_enough_children = len(self.children) >= self._get_list_index_to_show()
        return not is_at_bottom and not is_enough_children