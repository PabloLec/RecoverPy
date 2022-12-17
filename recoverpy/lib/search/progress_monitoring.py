from re import findall
from subprocess import check_output, DEVNULL
from time import sleep

from models.search_progress import SearchProgress


def monitor_search_progress(grep_pid: int, progress: SearchProgress):
    while True:
        output: str = check_output(
            ["progress", "-p", str(grep_pid)], stderr=DEVNULL
        ).decode("utf8")

        if not output:
            progress.progress_percent = 100.0
            return

        percent: list = findall(r"(\d+\.\d+)%", output)

        if not percent:
            continue

        progress.progress_percent = float(percent[0])
        sleep(0.5)
