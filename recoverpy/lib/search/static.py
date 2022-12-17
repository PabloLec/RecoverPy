import asyncio
from io import BufferedReader
from queue import Queue
from re import findall
from subprocess import DEVNULL, PIPE, Popen, check_output
from threading import Thread
from time import sleep
from typing import TYPE_CHECKING, Callable


from lib.helper import decode_result, get_inode, is_dependency_installed












def get_dd_output(partition: str, block_size: int, block_number: int) -> bytes:
    return check_output(
        [
            "dd",
            f"if={partition}",
            "count=1",
            "status=none",
            f"bs={block_size}",
            f"skip={block_number}",
        ]
    )
