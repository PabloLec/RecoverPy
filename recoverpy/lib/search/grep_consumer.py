from __future__ import annotations

from io import BufferedReader
from multiprocessing import Queue


def enqueue_grep_output(out: BufferedReader, queue: Queue[bytes]) -> None:
    for line in iter(out.readline, b""):
        queue.put(line)
    out.close()
