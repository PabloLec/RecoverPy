import errno
import stat
from types import SimpleNamespace

import pytest

from recoverpy.lib.storage.block_device_metadata import (
    BLKGETSIZE64, BLKPBSZGET, BLKROGET, BLKSSZGET, DeviceIOError,
    get_device_info, get_logical_block_size)


def test_get_device_info_fallback_for_regular_file(tmp_path):
    image = tmp_path / "disk.img"
    image.write_bytes(b"A" * 4096)

    info = get_device_info(str(image))

    assert info.is_block_device is False
    assert info.size_bytes == 4096
    assert info.logical_sector_size == 512
    assert info.physical_sector_size == 512


def test_get_device_info_block_device_ioctl_success(mocker):
    fd = 42
    mocker.patch("os.open", return_value=fd)
    mocker.patch("os.close")
    mocker.patch("os.fstat", return_value=SimpleNamespace(st_mode=stat.S_IFBLK))

    def fake_ioctl(_fd, request, data, _mutate):
        if request == BLKGETSIZE64:
            data[:] = (1024).to_bytes(8, "little")
        elif request == BLKSSZGET:
            data[:] = (4096).to_bytes(4, "little")
        elif request == BLKPBSZGET:
            data[:] = (8192).to_bytes(4, "little")
        elif request == BLKROGET:
            data[:] = (1).to_bytes(4, "little")
        return 0

    mocker.patch("fcntl.ioctl", side_effect=fake_ioctl)

    info = get_device_info("/dev/mock")

    assert info.is_block_device is True
    assert info.size_bytes == 1024
    assert info.logical_sector_size == 4096
    assert info.physical_sector_size == 8192
    assert info.read_only is True


def test_get_device_info_block_device_physical_ioctl_fallback(mocker):
    fd = 33
    mocker.patch("os.open", return_value=fd)
    mocker.patch("os.close")
    mocker.patch("os.fstat", return_value=SimpleNamespace(st_mode=stat.S_IFBLK))

    def fake_ioctl(_fd, request, data, _mutate):
        if request == BLKGETSIZE64:
            data[:] = (2048).to_bytes(8, "little")
            return 0
        if request == BLKSSZGET:
            data[:] = (512).to_bytes(4, "little")
            return 0
        if request == BLKROGET:
            data[:] = (0).to_bytes(4, "little")
            return 0
        if request == BLKPBSZGET:
            raise OSError(errno.EIO, "ioctl failure")
        return 0

    mocker.patch("fcntl.ioctl", side_effect=fake_ioctl)

    info = get_device_info("/dev/mock")
    assert info.physical_sector_size == 512


def test_get_logical_block_size_permission_error(mocker):
    mocker.patch("os.open", side_effect=PermissionError("denied"))

    with pytest.raises(DeviceIOError) as error:
        get_logical_block_size("/dev/sda1")

    assert "run as root" in error.value.user_message


def test_get_logical_block_size_ioctl_error(mocker):
    fd = 44
    mocker.patch("os.open", return_value=fd)
    mocker.patch("os.close")
    mocker.patch("os.fstat", return_value=SimpleNamespace(st_mode=stat.S_IFBLK))
    mocker.patch("fcntl.ioctl", side_effect=OSError(errno.EIO, "i/o"))

    with pytest.raises(DeviceIOError) as error:
        get_logical_block_size("/dev/sda1")

    assert "Cannot read device information" in error.value.user_message
