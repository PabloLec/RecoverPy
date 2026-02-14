"""A Textual ListView Widget for displaying partitions."""

from typing import Dict, Optional

from textual.widgets import Label, ListItem, ListView

from recoverpy.lib.storage.block_device_inventory import (DeviceDiscoveryError,
                                                          get_partitions)
from recoverpy.log.logger import log
from recoverpy.models.partition import Partition


def _get_label(partition: Partition) -> Label:
    display_type = (
        partition.fs_type
        if partition.fs_type != "unknown"
        else partition.device_type
    )
    label_content = f"{partition.name} | {display_type}"
    if partition.is_mounted:
        label_content += f" | Mounted on: {partition.mount_point}"
    return Label(label_content)


def _get_partition_id(partition: Partition) -> str:
    return "".join(filter(str.isalnum, partition.name))


class PartitionList(ListView):
    def __init__(self, *children, **kwargs) -> None:  # type: ignore
        super().__init__(id="partition-list", *children, **kwargs)
        self.list_items: Dict[Optional[str], Partition] = {}

    async def on_mount(self) -> None:
        await self.set_partitions()

    async def set_partitions(self, filtered: bool = True) -> None:
        try:
            partitions = get_partitions(filtered)
        except DeviceDiscoveryError as error:
            log.error(f"partition_list - {error}")
            if self.app:
                self.notify(str(error), severity="error")
            return

        await self.clear()
        self.list_items.clear()
        for partition in partitions:
            log.debug(f"partition_list - Appending partition {partition.name}")
            list_item = self._create_list_item(partition)
            self.list_items[list_item.id] = partition
            await self.append(list_item)

    def _create_list_item(self, partition: Partition) -> ListItem:
        list_item = ListItem(_get_label(partition), id=_get_partition_id(partition))
        if partition.is_mounted:
            list_item.add_class("mounted")
        return list_item
