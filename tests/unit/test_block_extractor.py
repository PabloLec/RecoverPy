import errno

import pytest

from recoverpy.lib.storage.byte_range_reader import (BlockExtractionError,
                                                     extract_range, read_block)


def test_extract_range_success(tmp_path):
    source = tmp_path / "disk.img"
    source.write_bytes(b"0123456789abcdef")
    output = tmp_path / "out.bin"

    extract_range(str(source), 4, 6, str(output), chunk_size=2)

    assert output.read_bytes() == b"456789"


def test_extract_range_invalid_range(tmp_path):
    source = tmp_path / "disk.img"
    source.write_bytes(b"abc")
    output = tmp_path / "out.bin"

    with pytest.raises(BlockExtractionError):
        extract_range(str(source), -1, 1, str(output))

    with pytest.raises(BlockExtractionError):
        extract_range(str(source), 0, 0, str(output))


def test_extract_range_permission_error(mocker, tmp_path):
    output = tmp_path / "out.bin"
    mocker.patch("os.open", side_effect=PermissionError("denied"))

    with pytest.raises(BlockExtractionError) as error:
        extract_range("/dev/sda1", 0, 10, str(output))

    assert "Permission denied" in error.value.user_message


def test_read_block_io_error(mocker):
    mocker.patch("os.open", return_value=42)
    mocker.patch(
        "os.pread",
        side_effect=OSError(errno.EIO, "I/O error"),
    )
    close_mock = mocker.patch("os.close")

    with pytest.raises(BlockExtractionError) as error:
        read_block("/dev/sda1", 4096, 0)

    assert "I/O error" in error.value.user_message
    close_mock.assert_called_once_with(42)
