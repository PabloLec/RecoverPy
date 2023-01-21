from recoverpy.lib.helper import get_block_size


class SearchParams:
    def __init__(self, partition: str, search_string: str):
        self.search_string = search_string
        self.partition = partition
        self.block_size = get_block_size(partition)
        self.searched_lines = search_string.strip().splitlines()
        self.is_multi_line = len(self.searched_lines) > 1
