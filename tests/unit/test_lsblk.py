from recoverpy.lib.lsblk import _IGNORED_PARTITION_TYPES, get_partitions
from tests.fixtures.mock_lsblk_output import (
    UNFILTERED_PARTITION_COUNT,
    VISIBLE_PARTITION_COUNT,
)


def test_get_partitions_filtered():
    partitions = get_partitions(True)

    assert len(partitions) == VISIBLE_PARTITION_COUNT
    for ignored_type in _IGNORED_PARTITION_TYPES:
        assert all(ignored_type not in partition.name for partition in partitions)


def test_get_partitions_unfiltered():
    partitions = get_partitions(False)

    assert len(partitions) == UNFILTERED_PARTITION_COUNT
