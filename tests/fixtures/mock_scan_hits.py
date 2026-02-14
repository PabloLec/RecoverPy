from recoverpy.lib.search.binary_scanner import ScanHit

SCAN_HIT_COUNT = 3

MOCK_SCAN_HITS = [
    ScanHit(
        match_offset=4096,
        preview=b"Lorem ipsum dolor sit amet, test consectetur adipiscing elit, sed do ",
    ),
    ScanHit(
        match_offset=8192,
        preview=b"Lorem ipsum dolor sit amet, test consectetur adipiscing elit, sed da ",
    ),
    ScanHit(
        match_offset=12288,
        preview=b"Lorem ipsum dolor sit amet, test consectetur adipiscing elit, sed du",
    ),
]


def mock_iter_scan_hits(*args, **kwargs):
    for hit in MOCK_SCAN_HITS:
        yield hit
