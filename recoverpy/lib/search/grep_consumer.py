from io import BufferedReader
from multiprocessing import Queue


def enqueue_grep_output(out: BufferedReader, queue: Queue):
    read_grep_buffer(out, queue)


def read_grep_buffer(out: BufferedReader, queue: Queue):
    for line in iter(out.readline, b""):
        queue.put(line)
    out.close()
