from subprocess import check_output
from typing import List, Optional, Tuple

from recoverpy.models.partition import Partition

_IGNORED_PARTITION_TYPES: Tuple[str, str] = (" loop ", "swap")


def get_partitions(filtered: bool) -> List[Partition]:
    lsblk_output: str = _fetch_lsblk_output()
    return _parse_lsblk_output(lsblk_output, filtered)


def _fetch_lsblk_output() -> str:
    return check_output(
        ["lsblk", "-r", "-n", "-o", "NAME,TYPE,FSTYPE,MOUNTPOINT"],
        encoding="utf-8",
    )


def _parse_lsblk_output(lsblk_output: str, filtered: bool) -> List[Partition]:
    partitions = [
        _parse_partition(line)
        for line in lsblk_output.splitlines()
        if not (
            filtered and any(ignored in line for ignored in _IGNORED_PARTITION_TYPES)
        )
    ]
    return [p for p in partitions if p]


def _parse_partition(line: str) -> Optional[Partition]:
    values = line.strip().split()

    if len(values) < 3:
        return None

    name, _, fs_type, *mount_info = values
    is_mounted = bool(mount_info)
    mount_point = mount_info[0] if mount_info else None

    return Partition(
        name=name,
        fs_type=fs_type,
        is_mounted=is_mounted,
        mount_point=mount_point,
    )
