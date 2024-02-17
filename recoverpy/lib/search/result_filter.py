from __future__ import annotations

from queue import Queue
from typing import List

from recoverpy.lib.helper import decode_result, get_dd_output, get_inode
from recoverpy.log.logger import log
from recoverpy.models.search_params import SearchParams


class ResultFilter:
    def __init__(self, search_params: SearchParams):
        self.search_params = search_params

    def filter_results(self, queue_object: Queue[bytes]) -> List[str]:
        """Consume raw grep results, filter out false positives and return valid results."""

        queue_list: List[bytes] = list(queue_object.queue)
        queue_size = len(queue_list)
        queue_object.queue.clear()
        if queue_size == 0:
            return []

        decoded_results: List[str] = [decode_result(r) for r in queue_list]

        if not self.search_params.is_multi_line:
            return decoded_results

        final_results = [
            result for result in decoded_results if self._is_result_valid(result)
        ]
        log.debug(f"result_processor - Found {len(final_results)} new results")
        return final_results

    def _is_result_valid(self, result: str) -> bool:
        """Check if result contains all searched lines."""
        inode = int(get_inode(result))
        block_factor = self.search_params.block_size * 8

        both_block_output = self._get_combined_block_output(inode, block_factor)
        return all(
            line in both_block_output for line in self.search_params.searched_lines
        )

    def _get_combined_block_output(self, inode: int, block_factor: int) -> str:
        """Get combined output of current and next block."""
        block_index = inode // block_factor
        block_output = get_dd_output(
            self.search_params.partition, block_factor, block_index
        )
        next_block_output = get_dd_output(
            self.search_params.partition, block_factor, block_index + 1
        )

        return decode_result(block_output) + decode_result(next_block_output)
