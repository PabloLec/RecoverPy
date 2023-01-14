from time import sleep

from recoverpy.models.search_progress import SearchProgress


def mock_monitor_search_progress(grep_pid: int, progress: SearchProgress) -> None:
    while True:
        progress.progress_percent = 100.0
        sleep(5)
