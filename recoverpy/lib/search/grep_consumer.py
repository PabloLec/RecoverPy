from __future__ import annotations

from io import BufferedReader
from multiprocessing import Queue

from recoverpy.log.logger import log


def enqueue_grep_output(out: BufferedReader, queue: Queue[bytes]) -> None:
    log.debug("grep_consumer - Grep output enqueue thread started")
    for line in iter(out.readline, b""):
        queue.put(line)
    out.close()
