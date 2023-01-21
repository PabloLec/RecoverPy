from __future__ import annotations

from queue import Queue
from typing import List

from recoverpy.lib.helper import decode_result, get_dd_output, get_inode
from recoverpy.models.search_params import SearchParams


class ResultProcessor:
    def __init__(self, search_params: SearchParams):
        self.search_params = search_params

    def get_new_results(self, queue_object: Queue[bytes]) -> List[str]:
        """Consume grep output queue and format results."""

        queue_list: List[bytes] = list(queue_object.queue)
        queue_size = len(queue_list)
        queue_object.queue.clear()
        if queue_size == 0:
            return []

        decoded_results: List[str] = [decode_result(r) for r in queue_list]

        if not self.search_params.is_multi_line:
            return decoded_results

        final_results = [
            result for result in decoded_results if self.is_result_format_valid(result)
        ]
        return final_results

    def is_result_format_valid(self, result: str) -> bool:
        """Check if all searched lines are present in result block and next adjacent
        block, else result is a false positive and will not be displayed.
        """

        inode: int = int(get_inode(result))
        block_output: bytes = get_dd_output(
            self.search_params.partition,
            self.search_params.block_size * 8,
            int(inode / (self.search_params.block_size * 8)),
        )
        next_block_output: bytes = get_dd_output(
            self.search_params.partition,
            self.search_params.block_size * 8,
            int(inode / (self.search_params.block_size * 8) + 1),
        )
        both_block_output: str = decode_result(block_output) + decode_result(
            next_block_output
        )
        return all(
            line in both_block_output for line in self.search_params.searched_lines
        )

    def fix_line_start(self, line: str) -> str:
        result_index: int = line.find(self.search_params.searched_lines[0])
        return line[min(result_index, 15) :]

    def fix_inode(self, inode: int) -> int:
        """Fix result block number if search string is too far from beginning of
        returned inode number.
        """

        inode = int(inode / self.search_params.block_size)

        for _ in range(10):
            dd_output: str = decode_result(
                get_dd_output(
                    self.search_params.partition, self.search_params.block_size, inode
                )
            )
            if self.search_params.searched_lines[0] in dd_output:
                return inode
            inode += 1
        return inode
