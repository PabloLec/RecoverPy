import errno
import os
from pathlib import Path


class BlockExtractionError(Exception):
    def __init__(self, message: str, user_message: str):
        super().__init__(message)
        self.user_message = user_message


def extract_range(
    source_path: str,
    offset: int,
    length: int,
    output_path: str,
    *,
    chunk_size: int = 1024 * 1024,
) -> None:
    _validate_range(offset, length, chunk_size)
    source_fd = _open_source(source_path)
    position = offset
    remaining = length

    try:
        with open(output_path, "wb") as output_file:
            while remaining > 0:
                to_read = min(chunk_size, remaining)
                chunk = _safe_pread(source_fd, to_read, position, source_path)
                if not chunk:
                    break
                output_file.write(chunk)
                read_len = len(chunk)
                remaining -= read_len
                position += read_len
    except PermissionError as error:
        raise BlockExtractionError(
            f"Cannot write output file {output_path}: {error}",
            f"Permission denied: cannot write {output_path}.",
        ) from error
    except OSError as error:
        raise BlockExtractionError(
            f"Cannot write output file {output_path}: {error}",
            f"Cannot write output file {output_path}.",
        ) from error
    finally:
        os.close(source_fd)

    if remaining > 0:
        raise BlockExtractionError(
            "Requested range exceeds available data.",
            f"Cannot read requested range from {source_path}: reached end of file/device.",
        )


def read_block(source_path: str, block_size: int, block_index: int) -> bytes:
    if block_size <= 0:
        raise BlockExtractionError(
            f"Invalid block size: {block_size}",
            "Invalid block size.",
        )
    if block_index < 0:
        raise BlockExtractionError(
            f"Invalid block index: {block_index}",
            "Invalid block index.",
        )
    return read_range(source_path, block_index * block_size, block_size)


def read_range(
    source_path: str, offset: int, length: int, *, chunk_size: int = 1024 * 1024
) -> bytes:
    _validate_range(offset, length, chunk_size)
    source_fd = _open_source(source_path)
    position = offset
    remaining = length
    chunks: list[bytes] = []

    try:
        while remaining > 0:
            to_read = min(chunk_size, remaining)
            chunk = _safe_pread(source_fd, to_read, position, source_path)
            if not chunk:
                break
            chunks.append(chunk)
            read_len = len(chunk)
            remaining -= read_len
            position += read_len
    finally:
        os.close(source_fd)

    if remaining > 0:
        raise BlockExtractionError(
            "Requested range exceeds available data.",
            f"Cannot read requested range from {source_path}: reached end of file/device.",
        )

    return b"".join(chunks)


def _open_source(source_path: str) -> int:
    try:
        return os.open(source_path, os.O_RDONLY)
    except PermissionError as error:
        raise BlockExtractionError(
            f"Cannot open source {source_path}: {error}",
            f"Permission denied: cannot open {source_path} (run as root).",
        ) from error
    except OSError as error:
        raise BlockExtractionError(
            f"Cannot open source {source_path}: {error}",
            _get_open_error_message(source_path, error),
        ) from error


def _safe_pread(source_fd: int, size: int, offset: int, source_path: str) -> bytes:
    try:
        return os.pread(source_fd, size, offset)
    except PermissionError as error:
        raise BlockExtractionError(
            f"Cannot read source {source_path}: {error}",
            f"Permission denied: cannot read {source_path} (run as root).",
        ) from error
    except OSError as error:
        raise BlockExtractionError(
            f"Cannot read source {source_path}: {error}",
            _get_read_error_message(source_path, error),
        ) from error


def _validate_range(offset: int, length: int, chunk_size: int) -> None:
    if offset < 0:
        raise BlockExtractionError(
            f"Invalid offset: {offset}",
            "Invalid offset: expected value >= 0.",
        )
    if length <= 0:
        raise BlockExtractionError(
            f"Invalid length: {length}",
            "Invalid length: expected value > 0.",
        )
    if chunk_size <= 0:
        raise BlockExtractionError(
            f"Invalid chunk size: {chunk_size}",
            "Invalid chunk size: expected value > 0.",
        )


def _get_open_error_message(source_path: str, error: OSError) -> str:
    if error.errno == errno.EIO:
        return f"Cannot open device {source_path} (I/O error)."
    if Path(source_path).exists():
        return f"Cannot access {source_path}."
    return f"Source {source_path} does not exist."


def _get_read_error_message(source_path: str, error: OSError) -> str:
    if error.errno == errno.EIO:
        return f"Cannot read device {source_path} (I/O error)."
    return f"Cannot read from {source_path}."
