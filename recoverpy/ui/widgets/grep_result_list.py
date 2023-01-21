"""A Textual ListView widget consuming an asyncio Queue"""

from __future__ import annotations

from asyncio import Lock, Queue, sleep
from typing import List, cast

from textual.widget import Widget
from textual.widgets import Label, ListView

from recoverpy.models.grep_result import GrepResult


class GrepResultList(ListView):
    list_items_background_color = {0: "red", 1: "green"}

    def __init__(self, *children, **kwargs) -> None:  # type: ignore
        super().__init__(*children, **kwargs)
        self.results: List[str] = []
        self.lock = Lock()
        self.grep_results: List[GrepResult] = []

    async def start_consumer(self, queue: Queue[GrepResult]) -> None:
        while True:
            if not self._should_add_more():
                await sleep(0.1)
                continue
            grep_result = await queue.get()
            await self._append(grep_result)

    async def _append(self, grep_result: GrepResult) -> None:
        if grep_result.list_item is None:
            return
        async with self.lock:
            self.grep_results.append(grep_result)
            self._resize_item(len(self.grep_results) - 1, grep_result.list_item)
            await super().append(grep_result.list_item)

    def _get_list_index_to_show(self) -> int:
        return self.size.height + int(self.scroll_y) + 10

    def _should_add_more(self) -> bool:
        return len(self.children) < self._get_list_index_to_show()

    def on_resize(self) -> None:
        for index, item in enumerate(self.children):
            self._resize_item(index, item)

    def _resize_item(self, index: int, item: Widget) -> None:
        max_item_width = self.size.width - self.size.width // 20
        grep_result_line = self.grep_results[index].line

        cast(Label, item.children[0]).update(grep_result_line[:max_item_width])
