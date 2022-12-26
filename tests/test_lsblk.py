from recoverpy.lib.lsblk import get_partitions, _IGNORED_PARTITIONS_TYPES


def test_get_partitions():
    """Test lsblk."""
    partitions = get_partitions()
    assert len(partitions) == 7

    for ignored_type in _IGNORED_PARTITIONS_TYPES:
        assert all(ignored_type not in partition.name for partition in partitions)
