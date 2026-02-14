import pytest

from recoverpy.lib.storage.block_device_inventory import (
    _IGNORED_PARTITION_TYPES, DeviceDiscoveryError, get_partitions)
from tests.fixtures.mock_device_discovery import (UNFILTERED_PARTITION_COUNT,
                                                  VISIBLE_PARTITION_COUNT)


def test_get_partitions_filtered():
    partitions = get_partitions(True)

    assert len(partitions) == VISIBLE_PARTITION_COUNT
    for ignored_type in _IGNORED_PARTITION_TYPES:
        assert all(ignored_type not in partition.name for partition in partitions)


def test_get_partitions_unfiltered():
    partitions = get_partitions(False)

    assert len(partitions) == UNFILTERED_PARTITION_COUNT


def test_get_partitions_permission_error(mocker):
    mocker.patch(
        "recoverpy.lib.storage.block_device_inventory._read_proc_mounts",
        side_effect=PermissionError("permission denied"),
    )

    with pytest.raises(DeviceDiscoveryError):
        get_partitions(True)
