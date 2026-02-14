import pytest
from textual.app import App, ComposeResult

from recoverpy.lib.device_discovery import DeviceDiscoveryError
from recoverpy.ui.widgets.partition_list import PartitionList


class PartitionListApp(App[None]):
    def compose(self) -> ComposeResult:
        yield PartitionList()


@pytest.mark.asyncio
async def test_partition_list_discovery_error_does_not_crash(mocker):
    mocker.patch(
        "recoverpy.ui.widgets.partition_list.get_partitions",
        side_effect=DeviceDiscoveryError("Cannot access mount/device info"),
    )

    async with PartitionListApp().run_test() as pilot:
        await pilot.pause()
        assert len(list(pilot.app.query("ListItem").results())) == 0
