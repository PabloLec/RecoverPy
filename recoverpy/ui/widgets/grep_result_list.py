"""A Textual ListView widget consuming an asyncio Queue"""

from __future__ import annotations

from asyncio import Lock, Queue, sleep
from typing import List, Optional, cast

from textual.widget import Widget
from textual.widgets import Label, ListView

from recoverpy.log.logger import log
from recoverpy.models.grep_result import GrepResult


class GrepResultList(ListView):
    list_items_background_color = {0: "red", 1: "green"}

    def __init__(self, *children, **kwargs) -> None:  # type: ignore
        super().__init__(*children, **kwargs)
        self.results: List[str] = []
        self.lock = Lock()
        self.grep_results: List[GrepResult] = []
        self.id = "grep-result-list"

    async def start_consumer(self, queue: Queue[GrepResult]) -> None:
        log.debug("grep_result_list - Starting consumer")
        while True:
            if not self._should_add_more():
                await sleep(0.1)
                continue
            grep_result = await queue.get()
            await self._append(grep_result)
        log.debug("grep_result_list - Consumer stopped")

    def get_index(self) -> int:
        list_index: Optional[int] = self.index
        return list_index if list_index else 0

    async def _append(self, grep_result: GrepResult) -> None:
        log.debug(f"grep_result_list - Appending inode {grep_result.inode}")
        if grep_result.list_item is None:
            log.error(
                f"grep_result_list - Grep result {grep_result.inode} has no list item"
            )
            return
        async with self.lock:
            self.grep_results.append(grep_result)
            self._resize_item(len(self.grep_results) - 1, grep_result.list_item)
            await super().append(grep_result.list_item)

    def _get_list_index_to_show(self) -> int:
        return int(self.size.height) + int(self.scroll_y) + 10

    def _should_add_more(self) -> bool:
        return len(self.children) < self._get_list_index_to_show()

    def on_resize(self) -> None:
        for index, item in enumerate(self.children):
            self._resize_item(index, item)

    def _resize_item(self, index: int, item: Widget) -> None:
        max_item_width = self.size.width - self.size.width // 20
        grep_result_line = self.grep_results[index].line

        cast(Label, item.children[0]).update(grep_result_line[:max_item_width])
