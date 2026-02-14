"""
SearchEngine orchestrates native scan workers and streams formatted results to the UI.
"""

from __future__ import annotations

from asyncio import AbstractEventLoop
from asyncio import Queue as AsyncQueue
from asyncio import new_event_loop
from collections import OrderedDict
from queue import Empty, Full, Queue
from threading import Event, Thread
from time import monotonic, sleep
from typing import Iterable, Optional

from recoverpy.lib.storage.byte_range_reader import BlockExtractionError, read_block
from recoverpy.lib.storage.block_device_metadata import get_device_info
from recoverpy.lib.text.text_processing import decode_result, get_printable
from recoverpy.lib.search.binary_scanner import ScanError, ScanHit, iter_scan_hits
from recoverpy.log.logger import log
from recoverpy.models.search_result import SearchResult
from recoverpy.models.search_params import SearchParams
from recoverpy.models.search_progress import SearchProgress

_RAW_HITS_QUEUE_MAXSIZE = 4000
_RECENT_BLOCKS_MAXSIZE = 8192
_BATCH_MAX_ITEMS = 100
_BATCH_MAX_WAIT_SECONDS = 0.2


class SearchEngine:
    def __init__(self, partition: str, searched_string: str):
        self.search_params = SearchParams(partition, searched_string)
        self.search_progress = SearchProgress()
        self.formatted_results_queue: AsyncQueue[SearchResult] = AsyncQueue()
        self.raw_scan_hits_queue: Queue[Optional[ScanHit]] = Queue(
            maxsize=_RAW_HITS_QUEUE_MAXSIZE
        )

        device_info = get_device_info(partition)
        self._source_size_bytes = max(1, device_info.size_bytes)
        self._stop_event = Event()
        self._pause_event = Event()
        self._scan_thread: Thread | None = None
        self._convert_thread: Thread | None = None
        self._recent_blocks: OrderedDict[int, None] = OrderedDict()

    async def start_search(self) -> None:
        self._start_workers()

    def stop_search(self) -> None:
        self._stop_event.set()
        self._pause_event.clear()
        self._enqueue_sentinel()
        if self._scan_thread and self._scan_thread.is_alive():
            self._scan_thread.join(timeout=1.0)
        if self._convert_thread and self._convert_thread.is_alive():
            self._convert_thread.join(timeout=1.0)

    def pause_search(self) -> None:
        self._pause_event.set()

    def resume_search(self) -> None:
        self._pause_event.clear()

    def is_paused(self) -> bool:
        return self._pause_event.is_set()

    def _start_workers(self) -> None:
        self._scan_thread = Thread(
            target=self._scan_hits_worker,
            daemon=True,
            name="scan-hits-worker",
        )
        self._convert_thread = Thread(
            target=self._convert_hits_worker,
            daemon=True,
            name="convert-hits-worker",
        )
        self._scan_thread.start()
        self._convert_thread.start()

    def _scan_hits_worker(self) -> None:
        needle = self.search_params.searched_lines[0].encode("utf-8")
        bytes_read = 0
        last_progress_update = 0.0
        try:
            for hit in iter_scan_hits(
                self.search_params.partition,
                needle,
                stop_event=self._stop_event,
                pause_event=self._pause_event,
            ):
                if self._stop_event.is_set():
                    break

                while not self._stop_event.is_set():
                    try:
                        self.raw_scan_hits_queue.put(hit, timeout=0.1)
                        break
                    except Full:
                        continue

                # Approximate native progress: scanner is sequential so the furthest
                # match offset is a lower bound of bytes already read.
                bytes_read = max(bytes_read, hit.match_offset + len(needle))
                now = monotonic()
                if now - last_progress_update >= 0.2:
                    self._set_progress(bytes_read)
                    last_progress_update = now

            self._set_progress(self._source_size_bytes)
        except ScanError as error:
            log.error(f"search_engine - {error}")
            self.search_progress.error_message = error.user_message
            self.search_progress.progress_percent = 100.0
        except Exception as error:  # pragma: no cover - safety net
            log.error(f"search_engine - Unexpected scanner error: {error}")
            self.search_progress.error_message = "Unexpected scanning error."
            self.search_progress.progress_percent = 100.0
        finally:
            self._enqueue_sentinel()

    def _enqueue_sentinel(self) -> None:
        while True:
            try:
                self.raw_scan_hits_queue.put_nowait(None)
                return
            except Full:
                try:
                    self.raw_scan_hits_queue.get_nowait()
                except Empty:
                    continue

    def _set_progress(self, bytes_read: int) -> None:
        if self._source_size_bytes <= 0:
            self.search_progress.progress_percent = 100.0
            return
        ratio = min(1.0, max(0.0, bytes_read / self._source_size_bytes))
        self.search_progress.progress_percent = ratio * 100

    def _convert_hits_worker(self) -> None:
        loop = new_event_loop()
        producer_done = False
        try:
            while not producer_done:
                batch: list[ScanHit] = []
                deadline = monotonic() + _BATCH_MAX_WAIT_SECONDS

                while len(batch) < _BATCH_MAX_ITEMS and monotonic() < deadline:
                    timeout = max(0.01, deadline - monotonic())
                    try:
                        item = self.raw_scan_hits_queue.get(timeout=timeout)
                    except Empty:
                        continue

                    if item is None:
                        producer_done = True
                        break
                    batch.append(item)

                if batch:
                    self._process_hits_batch(batch, loop)
        except Exception as error:  # pragma: no cover - safety net
            log.error(f"search_engine - Unexpected converter error: {error}")
            self.search_progress.error_message = "Unexpected result processing error."
        finally:
            self.search_progress.progress_percent = 100.0

    def _process_hits_batch(
        self, hits: Iterable[ScanHit], loop: AbstractEventLoop
    ) -> None:
        for hit in hits:
            inode = hit.match_offset // self.search_params.block_size

            if self._is_recent_block(inode):
                continue

            if self.search_params.is_multi_line and not self._is_hit_valid_multiline(hit):
                continue

            preview_line = self._format_preview(hit.preview)
            search_result = SearchResult(preview_line, inode=inode)
            search_result.css_class = (
                "search-result-odd"
                if self.search_progress.result_count % 2 == 0
                else "search-result-even"
            )

            loop.run_until_complete(self.formatted_results_queue.put(search_result))
            self.search_progress.result_count += 1
            self._mark_recent_block(inode)

    def _is_hit_valid_multiline(self, hit: ScanHit) -> bool:
        block_factor = self.search_params.block_size * 8
        block_index = hit.match_offset // block_factor

        try:
            current_block = read_block(
                self.search_params.partition,
                block_factor,
                block_index,
            )
            next_block = read_block(
                self.search_params.partition,
                block_factor,
                block_index + 1,
            )
        except BlockExtractionError as error:
            log.warning(f"search_engine - {error}")
            return False

        content = decode_result(current_block) + decode_result(next_block)
        return all(line in content for line in self.search_params.searched_lines)

    def _format_preview(self, preview: bytes) -> str:
        return get_printable(decode_result(preview))

    def _is_recent_block(self, block_index: int) -> bool:
        return block_index in self._recent_blocks

    def _mark_recent_block(self, block_index: int) -> None:
        self._recent_blocks[block_index] = None
        self._recent_blocks.move_to_end(block_index)
        if len(self._recent_blocks) > _RECENT_BLOCKS_MAXSIZE:
            self._recent_blocks.popitem(last=False)
