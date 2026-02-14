"""Low-level block device metadata access via Linux ioctl with safe fallbacks."""

import fcntl
import os
import stat
import struct
from dataclasses import dataclass

# Linux block ioctl request numbers.
# They are stable kernel ABI constants and intentionally kept explicit here.
BLKGETSIZE64 = 0x80081272
BLKSSZGET = 0x1268
BLKPBSZGET = 0x127B
BLKROGET = 0x125E

_DEFAULT_SECTOR_SIZE = 512


class DeviceIOError(Exception):
    def __init__(self, message: str, user_message: str):
        super().__init__(message)
        self.user_message = user_message


@dataclass
class DeviceInfo:
    size_bytes: int
    logical_sector_size: int
    physical_sector_size: int
    read_only: bool
    is_block_device: bool


def get_logical_block_size(path: str) -> int:
    return get_device_info(path).logical_sector_size


def get_device_info(path: str) -> DeviceInfo:
    fd = _open_read_only(path)
    try:
        file_stat = os.fstat(fd)
        if stat.S_ISBLK(file_stat.st_mode):
            return _get_block_device_info(fd, path)
    finally:
        os.close(fd)

    return _get_file_fallback_info(path)


def _open_read_only(path: str) -> int:
    try:
        return os.open(path, os.O_RDONLY)
    except PermissionError as error:
        raise DeviceIOError(
            f"Cannot open {path}: {error}",
            f"Permission denied: cannot open {path} (run as root).",
        ) from error
    except OSError as error:
        raise DeviceIOError(
            f"Cannot open {path}: {error}",
            f"Cannot access {path}.",
        ) from error


def _get_block_device_info(fd: int, path: str) -> DeviceInfo:
    try:
        size_bytes = _ioctl_get_u64(fd, BLKGETSIZE64)
        logical_sector_size = _ioctl_get_u32(fd, BLKSSZGET)
        read_only = bool(_ioctl_get_u32(fd, BLKROGET))
    except PermissionError as error:
        raise DeviceIOError(
            f"Cannot read block metadata from {path}: {error}",
            f"Permission denied: cannot read {path} metadata (run as root).",
        ) from error
    except OSError as error:
        raise DeviceIOError(
            f"Cannot read block metadata from {path}: {error}",
            f"Cannot read device information from {path}.",
        ) from error

    try:
        physical_sector_size = _ioctl_get_u32(fd, BLKPBSZGET)
    except (PermissionError, OSError):
        # Some devices/filesystems do not expose physical block size cleanly.
        # Falling back to logical size keeps the rest of the pipeline usable.
        physical_sector_size = logical_sector_size

    return DeviceInfo(
        size_bytes=size_bytes,
        logical_sector_size=logical_sector_size,
        physical_sector_size=physical_sector_size,
        read_only=read_only,
        is_block_device=True,
    )


def _get_file_fallback_info(path: str) -> DeviceInfo:
    try:
        file_size = os.stat(path).st_size
    except PermissionError as error:
        raise DeviceIOError(
            f"Cannot stat {path}: {error}",
            f"Permission denied: cannot read {path} (run as root).",
        ) from error
    except OSError as error:
        raise DeviceIOError(
            f"Cannot stat {path}: {error}",
            f"Cannot access {path}.",
        ) from error

    return DeviceInfo(
        size_bytes=file_size,
        logical_sector_size=_DEFAULT_SECTOR_SIZE,
        physical_sector_size=_DEFAULT_SECTOR_SIZE,
        read_only=not os.access(path, os.W_OK),
        is_block_device=False,
    )


def _ioctl_get_u32(fd: int, request: int) -> int:
    data = bytearray(4)
    fcntl.ioctl(fd, request, data, True)
    return struct.unpack("<I", data)[0]


def _ioctl_get_u64(fd: int, request: int) -> int:
    data = bytearray(8)
    fcntl.ioctl(fd, request, data, True)
    return struct.unpack("<Q", data)[0]
