from recoverpy.lib.lsblk import _IGNORED_PARTITION_TYPES, get_partitions
from tests.fixtures.mock_lsblk_output import VISIBLE_PARTITION_COUNT


def test_get_partitions():
    partitions = get_partitions()

    assert len(partitions) == VISIBLE_PARTITION_COUNT
    for ignored_type in _IGNORED_PARTITION_TYPES:
        assert all(ignored_type not in partition.name for partition in partitions)
