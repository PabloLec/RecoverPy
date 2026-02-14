"""
Streaming binary scanner for devices and disk images.

This module performs chunked byte-pattern scanning without loading the full source
in memory. It emits lightweight `ScanHit` records containing the absolute match
offset and a bounded preview window around each match.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from threading import Event
from time import sleep
from typing import Iterator

DEFAULT_SCAN_CHUNK_SIZE = 8 * 1024 * 1024
DEFAULT_PREVIEW_BEFORE_BYTES = 256
DEFAULT_PREVIEW_AFTER_BYTES = 256
DEFAULT_MAX_PREVIEW_BYTES = 512
PAUSE_POLL_INTERVAL_SECONDS = 0.25


@dataclass(frozen=True)
class ScanHit:
    match_offset: int
    preview: bytes


class ScanError(Exception):
    def __init__(self, message: str, user_message: str):
        super().__init__(message)
        self.user_message = user_message


def iter_scan_hits(
    source_path: str,
    needle: bytes,
    *,
    chunk_size: int = DEFAULT_SCAN_CHUNK_SIZE,
    preview_before: int = DEFAULT_PREVIEW_BEFORE_BYTES,
    preview_after: int = DEFAULT_PREVIEW_AFTER_BYTES,
    max_preview_len: int = DEFAULT_MAX_PREVIEW_BYTES,
    stop_event: Event | None = None,
    pause_event: Event | None = None,
) -> Iterator[ScanHit]:
    if not needle:
        raise ValueError("needle must not be empty")
    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")
    if preview_before < 0 or preview_after < 0:
        raise ValueError("preview sizes must be >= 0")
    if max_preview_len <= 0:
        raise ValueError("max_preview_len must be > 0")

    # Keep enough trailing bytes from the previous chunk so matches crossing
    # chunk boundaries are still detected in the next iteration.
    overlap = max(0, len(needle) - 1)
    tail_size = max(overlap, preview_before)
    preview_window = min(max_preview_len, preview_before + preview_after)

    try:
        fd = os.open(source_path, os.O_RDONLY)
    except PermissionError as error:
        raise ScanError(
            f"Cannot open scan source {source_path}: {error}",
            f"Permission denied opening {source_path} (run as root).",
        ) from error
    except OSError as error:
        raise ScanError(
            f"Cannot open scan source {source_path}: {error}",
            f"Cannot open {source_path}.",
        ) from error

    offset = 0
    tail = b""
    try:
        while True:
            if stop_event and stop_event.is_set():
                return
            while pause_event and pause_event.is_set():
                if stop_event and stop_event.is_set():
                    return
                sleep(PAUSE_POLL_INTERVAL_SECONDS)
            try:
                chunk = os.read(fd, chunk_size)
            except PermissionError as error:
                raise ScanError(
                    f"Permission denied while reading {source_path}: {error}",
                    f"Permission denied reading {source_path} (run as root).",
                ) from error
            except OSError as error:
                raise ScanError(
                    f"I/O error while reading {source_path}: {error}",
                    f"I/O error reading {source_path}.",
                ) from error

            if not chunk:
                return

            buffer = tail + chunk
            buffer_start_offset = offset - len(tail)
            min_new_match_offset = max(0, offset - overlap)

            search_index = 0
            while True:
                match_index = buffer.find(needle, search_index)
                if match_index < 0:
                    break

                absolute_match_offset = buffer_start_offset + match_index
                search_index = match_index + 1
                # Skip offsets that belong to the previous chunk overlap;
                # this prevents duplicate hits while preserving boundary matches.
                if absolute_match_offset < min_new_match_offset:
                    continue

                preview = _read_preview(
                    fd=fd,
                    match_offset=absolute_match_offset,
                    before=preview_before,
                    after=preview_after,
                    max_len=preview_window,
                )
                yield ScanHit(match_offset=absolute_match_offset, preview=preview)

            offset += len(chunk)
            if tail_size > 0:
                tail = buffer[-tail_size:]
            else:
                tail = b""
    finally:
        os.close(fd)


def _read_preview(
    *,
    fd: int,
    match_offset: int,
    before: int,
    after: int,
    max_len: int,
) -> bytes:
    preview_start = max(0, match_offset - before)
    preview_end = match_offset + after
    to_read = max(0, min(max_len, preview_end - preview_start))
    if to_read <= 0:
        return b""
    return os.pread(fd, to_read, preview_start)
