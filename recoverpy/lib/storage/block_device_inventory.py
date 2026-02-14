"""Linux block device and partition inventory discovery."""

from pathlib import Path
from typing import Dict, List, Optional, Tuple

from recoverpy.models.partition import Partition

_SECTOR_SIZE = 512
_IGNORED_PARTITION_TYPES: Tuple[str, str] = ("loop", "swap")


class DeviceDiscoveryError(Exception):
    """Raised when block device discovery fails."""


def get_partitions(filtered: bool) -> List[Partition]:
    try:
        mount_info = _read_proc_mounts()
        proc_sizes = _read_proc_partition_sizes()
        block_devices = _list_block_devices()
    except (OSError, PermissionError) as error:
        raise DeviceDiscoveryError(
            f"Cannot access mount/device info: {error}"
        ) from error

    partitions: List[Partition] = []
    for name in block_devices:
        partition = _build_partition(name, mount_info, proc_sizes)
        if partition is None:
            continue
        if filtered and _is_ignored(partition):
            continue
        partitions.append(partition)

    return partitions


def _read_proc_mounts() -> Dict[str, List[Tuple[str, str]]]:
    mounts: Dict[str, List[Tuple[str, str]]] = {}
    with open("/proc/mounts", "r", encoding="utf-8") as mounts_file:
        for line in mounts_file:
            values = line.split()
            if len(values) < 3:
                continue

            source, mount_point, fs_type = values[0], values[1], values[2]
            if not source.startswith("/dev/"):
                continue

            mounts.setdefault(source, []).append((mount_point, fs_type))

    return mounts


def _read_proc_partition_sizes() -> Dict[str, int]:
    sizes: Dict[str, int] = {}
    with open("/proc/partitions", "r", encoding="utf-8") as partitions_file:
        for line in partitions_file:
            values = line.split()
            if len(values) != 4 or values[0] == "major":
                continue

            blocks, name = values[2], values[3]
            if not blocks.isdigit():
                continue
            sizes[name] = int(blocks) * 1024

    return sizes


def _list_block_devices() -> List[str]:
    return sorted(path.name for path in Path("/sys/class/block").iterdir())


def _build_partition(
    name: str,
    mount_info: Dict[str, List[Tuple[str, str]]],
    proc_sizes: Dict[str, int],
) -> Optional[Partition]:
    device_path = f"/dev/{name}"
    mounts = mount_info.get(device_path, [])
    is_mounted = len(mounts) > 0
    mount_point = mounts[0][0] if is_mounted else None
    fs_type = mounts[0][1] if is_mounted else "unknown"

    device_type = _read_device_type(name) or "unknown"
    size_bytes = _read_size_bytes(name, proc_sizes)

    # Keep existing UX behavior: do not show unmounted plain disks.
    if device_type == "disk" and not is_mounted:
        return None

    return Partition(
        name=name,
        fs_type=fs_type,
        is_mounted=is_mounted,
        mount_point=mount_point,
        size_bytes=size_bytes,
        device_type=device_type,
        device_path=device_path,
    )


def _read_device_type(name: str) -> Optional[str]:
    uevent_path = Path("/sys/class/block") / name / "uevent"
    try:
        with open(uevent_path, "r", encoding="utf-8") as uevent_file:
            for line in uevent_file:
                if line.startswith("DEVTYPE="):
                    return line.strip().split("=", maxsplit=1)[1]
    except (FileNotFoundError, PermissionError, OSError):
        return None
    return None


def _read_size_bytes(name: str, proc_sizes: Dict[str, int]) -> int:
    size_path = Path("/sys/class/block") / name / "size"
    try:
        with open(size_path, "r", encoding="utf-8") as size_file:
            sectors = int(size_file.read().strip())
            return sectors * _SECTOR_SIZE
    except (FileNotFoundError, PermissionError, OSError, ValueError):
        return proc_sizes.get(name, 0)


def _is_ignored(partition: Partition) -> bool:
    if partition.name.startswith(_IGNORED_PARTITION_TYPES[0]):
        return True
    if partition.fs_type == _IGNORED_PARTITION_TYPES[1]:
        return True
    return False
