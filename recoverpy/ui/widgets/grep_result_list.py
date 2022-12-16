import asyncio
from random import randint

from textual.widgets import ListView, ListItem, Label

from lib.helper import get_printable

from lib.search.grep_result import GrepResult


class GrepResultList(ListView):
    def __init__(self, *children, **kwargs):
        super().__init__(*children, **kwargs)
        self.results = []
        self.lock = asyncio.Lock()

    async def start_consumer(self, queue: asyncio.Queue):
        while True:
            if not self._should_add_more():
                await asyncio.sleep(0.1)
                continue
            grep_result = await queue.get()
            await self.append(grep_result)

    async def append(self, grep_result: GrepResult) -> None:
        await super().append(grep_result.list_item)

    def _get_list_index_to_show(self) -> int:
        size_with_overflow = self.size.height + int(self.scroll_y) + 10
        return size_with_overflow

    def _should_add_more(self) -> bool:
        return len(self.children) < self._get_list_index_to_show()