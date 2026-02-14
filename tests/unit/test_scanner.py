from threading import Event

from recoverpy.lib.search.scanner import iter_scan_hits


def test_scan_offsets_are_exact(tmp_path):
    needle = b"NEEDLE"
    payload = bytearray(b"x" * 3000)
    expected_offsets = [10, 512, 1023, 2048]
    for offset in expected_offsets:
        payload[offset : offset + len(needle)] = needle

    source = tmp_path / "scan.bin"
    source.write_bytes(bytes(payload))

    hits = list(iter_scan_hits(str(source), needle, chunk_size=256))
    found_offsets = [hit.match_offset for hit in hits]

    assert found_offsets == expected_offsets


def test_scan_finds_match_crossing_chunk_boundary(tmp_path):
    needle = b"ABCDE12345"
    chunk_size = 64
    payload = bytearray(b"x" * 256)
    # Match starts near the end of the first chunk and spans across the boundary.
    start = chunk_size - 4
    payload[start : start + len(needle)] = needle

    source = tmp_path / "boundary.bin"
    source.write_bytes(bytes(payload))

    hits = list(iter_scan_hits(str(source), needle, chunk_size=chunk_size))

    assert len(hits) == 1
    assert hits[0].match_offset == start


def test_scan_preview_is_bounded_and_centered(tmp_path):
    needle = b"TOKEN"
    payload = bytearray(b"A" * 4096)
    offset = 2000
    payload[offset : offset + len(needle)] = needle

    source = tmp_path / "preview.bin"
    source.write_bytes(bytes(payload))

    hits = list(
        iter_scan_hits(
            str(source),
            needle,
            chunk_size=512,
            preview_before=400,
            preview_after=400,
            max_preview_len=512,
        )
    )
    assert len(hits) == 1

    preview = hits[0].preview
    assert len(preview) == 512
    assert needle in preview


def test_scan_cancel_stops_quickly(tmp_path):
    needle = b"HIT"
    chunk_size = 1024
    payload = bytearray(b"x" * (chunk_size * 20))
    for i in range(20):
        start = i * chunk_size
        payload[start : start + len(needle)] = needle
    source = tmp_path / "cancel.bin"
    source.write_bytes(bytes(payload))
    stop_event = Event()

    generator = iter_scan_hits(
        str(source),
        needle,
        chunk_size=chunk_size,
        stop_event=stop_event,
    )

    first_hit = next(generator)
    assert first_hit.match_offset == 0

    stop_event.set()
    remaining = list(generator)
    # Scanner may finish the current chunk before stop check, but must stop quickly.
    assert len(remaining) <= 1
