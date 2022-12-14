from textual.widgets import ListView, ListItem, Label

from lib.lsblk import get_partitions

from models.partition import Partition


def _get_label(partition: Partition):
    return Label(f"{partition.name} | {partition.fs_type} | {partition.is_mounted} | {partition.mount_point}")


class PartitionList(ListView):
    def __init__(self, *children, **kwargs):
        super().__init__(*children, **kwargs)
        self.list_items = {}
        self._append_partitions()

    def _append_partitions(self):
        for partition in get_partitions():
            list_item = ListItem(_get_label(partition))
            self.list_items[list_item.id] = partition
            self.append(list_item)
