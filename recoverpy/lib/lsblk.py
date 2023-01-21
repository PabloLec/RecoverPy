from subprocess import check_output
from typing import List, Tuple

from recoverpy.models.partition import Partition

_IGNORED_PARTITIONS_TYPES: Tuple[str, str] = (" loop ", "swap")


def get_partitions() -> List[Partition]:
    lsblk_output: str = _lsblk()
    return _format_lsblk_output(lsblk_output)


def _lsblk() -> str:
    return check_output(
        ["lsblk", "-r", "-n", "-o", "NAME,TYPE,FSTYPE,MOUNTPOINT"],
        encoding="utf-8",
    )


def _format_lsblk_output(lsblk_output: str) -> List[Partition]:
    partitions = []

    for line in lsblk_output.splitlines():
        if any(word in line for word in _IGNORED_PARTITIONS_TYPES):
            continue

        values = line.strip().split()

        if len(values) < 3:
            # Ignore if no FSTYPE detected
            continue

        if len(values) < 4:
            is_mounted = False
            mount_point = None
        else:
            is_mounted = True
            mount_point = values[3]

        partitions.append(
            Partition(
                name=values[0],
                fs_type=values[2],
                is_mounted=is_mounted,
                mount_point=mount_point,
            )
        )

    return partitions
