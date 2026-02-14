"""A Textual ListView widget consuming an asyncio Queue"""

from __future__ import annotations

from asyncio import Lock, Queue, sleep
from typing import List, cast

from textual.widgets import Label, ListView

from recoverpy.log.logger import log
from recoverpy.models.search_result import SearchResult


class SearchResultList(ListView):
    def __init__(self, *children, **kwargs) -> None:  # type: ignore
        super().__init__(*children, **kwargs)
        self.results: List[str] = []
        self.lock = Lock()
        self.search_results: List[SearchResult] = []
        self.id = "search-result-list"

    async def start_consumer(self, queue: Queue[SearchResult]) -> None:
        log.debug("search_result_list - Starting consumer")
        while True:
            if not self._should_add_more():
                await sleep(0.1)
                continue

            log.debug("search_result_list - Adding more results")
            search_result = await queue.get()
            await self._append(search_result)

    def get_index(self) -> int:
        return self.index or 0

    async def _append(self, search_result: SearchResult) -> None:
        log.debug(f"search_result_list - Appending inode {search_result.inode}")
        search_result.create_list_item()

        if not search_result.list_item:
            log.error(
                f"search_result_list - Search result {search_result.inode} has no list item"
            )
            return

        async with self.lock:
            self.search_results.append(search_result)
            new_index = len(self.search_results) - 1
            self._resize_item(new_index)
            await super().append(search_result.list_item)

    def _get_list_index_to_show(self) -> int:
        return int(self.size.height) + int(self.scroll_y) + 10

    def _should_add_more(self) -> bool:
        return len(self.children) < self._get_list_index_to_show()

    def on_resize(self) -> None:
        for index in range(len(self.children)):
            self._resize_item(index)

    def _resize_item(self, index: int) -> None:
        max_item_width = self.size.width - self.size.width // 20
        search_result_line = self.search_results[index].line
        cast(Label, self.search_results[index].label).update(
            search_result_line[:max_item_width]
        )
