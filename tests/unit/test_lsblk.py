from recoverpy.lib.lsblk import _IGNORED_PARTITIONS_TYPES, get_partitions


def test_get_partitions():
    partitions = get_partitions()

    assert len(partitions) == 7
    for ignored_type in _IGNORED_PARTITIONS_TYPES:
        assert all(ignored_type not in partition.name for partition in partitions)
