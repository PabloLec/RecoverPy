"""A Textual ListView Widget for displaying partitions."""

from textual.widgets import Label, ListItem, ListView

from recoverpy.lib.lsblk import get_partitions
from recoverpy.models.partition import Partition


def _get_label(partition: Partition):
    label_content = f"{partition.name} | {partition.fs_type}"
    if partition.is_mounted:
        label_content += f" | Mounted on: {partition.mount_point}"
    return Label(label_content)


class PartitionList(ListView):
    def __init__(self, *children, **kwargs):
        super().__init__(*children, **kwargs)
        self.list_items = {}
        self._append_partitions()

    def _append_partitions(self):
        for partition in get_partitions():
            list_item = ListItem(_get_label(partition), id=partition.name)
            if partition.is_mounted:
                list_item.add_class("mounted")
            self.list_items[list_item.id] = partition
            self.append(list_item)
