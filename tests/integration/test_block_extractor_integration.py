from recoverpy.lib.storage.byte_range_reader import extract_range, read_range


def test_extract_range_from_fake_disk_image(tmp_path):
    source = tmp_path / "fake_disk.img"
    data = bytearray(b"\x00" * 8192)
    pattern = b"RECOVERPY_PATTERN_2026"
    start = 4096 + 123
    data[start : start + len(pattern)] = pattern
    source.write_bytes(bytes(data))

    output = tmp_path / "range.bin"
    extract_range(str(source), 4096, 512, str(output), chunk_size=128)

    extracted = output.read_bytes()
    assert len(extracted) == 512
    assert pattern in extracted


def test_read_range_exact_bytes_from_fake_disk_image(tmp_path):
    source = tmp_path / "fake_disk.img"
    payload = b"A" * 128 + b"HELLO_RECOVERPY" + b"B" * 128
    source.write_bytes(payload)

    chunk = read_range(str(source), 120, 40, chunk_size=16)
    assert chunk == payload[120:160]
