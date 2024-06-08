"""A Textual ListView Widget for displaying partitions."""

from typing import Dict, Optional

from textual.events import Mount
from textual.widgets import Label, ListItem, ListView

from recoverpy.lib.lsblk import get_partitions
from recoverpy.log.logger import log
from recoverpy.models.partition import Partition


def _get_label(partition: Partition) -> Label:
    label_content = f"{partition.name} | {partition.fs_type}"
    if partition.is_mounted:
        label_content += f" | Mounted on: {partition.mount_point}"
    return Label(label_content)


def _get_partition_id(partition: Partition) -> str:
    return "".join(filter(str.isalnum, partition.name))


class PartitionList(ListView):
    def __init__(self, *children, **kwargs) -> None:  # type: ignore
        super().__init__(id="partition-list", *children, **kwargs)
        self.list_items: Dict[Optional[str], Partition] = {}

    def _on_mount(self, _: Mount) -> None:
        self._append_partitions()
        return super()._on_mount(_)

    def _append_partitions(self) -> None:
        for partition in get_partitions():
            log.debug(f"partition_list - Appending partition {partition.name}")
            list_item = self._create_list_item(partition)
            self.list_items[list_item.id] = partition
            self.append(list_item)

    def _create_list_item(self, partition: Partition) -> ListItem:
        list_item = ListItem(_get_label(partition), id=_get_partition_id(partition))
        if partition.is_mounted:
            list_item.add_class("mounted")
        return list_item
