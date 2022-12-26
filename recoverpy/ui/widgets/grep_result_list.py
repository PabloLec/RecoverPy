import asyncio

from textual._types import MessageTarget
from textual.message import Message
from textual.widgets import ListView, ListItem, Label

from models.grep_result import GrepResult


class GrepResultList(ListView):
    list_items_background_color = {0: "red", 1: "green"}

    def __init__(self, *children, **kwargs):
        super().__init__(*children, **kwargs)
        self.results = []
        self.lock = asyncio.Lock()
        self.grep_results = []

    async def start_consumer(self, queue: asyncio.Queue):
        while True:
            if not self._should_add_more():
                await asyncio.sleep(0.1)
                continue
            grep_result = await queue.get()
            await self.append(grep_result)

    async def append(self, grep_result: GrepResult) -> None:
        async with self.lock:
            self.grep_results.append(grep_result)
            self._resize_item(len(self.grep_results) - 1, grep_result.list_item)
            await super().append(grep_result.list_item)

    def _get_list_index_to_show(self) -> int:
        size_with_overflow = self.size.height + int(self.scroll_y) + 10
        return size_with_overflow

    def _should_add_more(self) -> bool:
        return len(self.children) < self._get_list_index_to_show()

    def on_resize(self) -> None:
        for index, item in enumerate(self.children):
            self._resize_item(index, item)

    def _resize_item(self, index: int, item: ListItem) -> None:
        max_item_width = self.size.width - self.size.width // 20
        grep_result_line = self.grep_results[index].line

        item.children[0].update(grep_result_line[:max_item_width])
