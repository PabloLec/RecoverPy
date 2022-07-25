from datetime import datetime
from logging import DEBUG, FileHandler
from logging import Logger as _Logger
from logging import getLogger
from pathlib import Path
from typing import Optional

from recoverpy.lib.meta_singleton import SingletonMeta


class Logger(metaclass=SingletonMeta):
    """Logging wrapper object."""

    def __init__(self):
        self.log_path: Optional[Path] = None
        self.log_enabled: bool = False
        self._logger = None

    def start_logging(self):
        time = datetime.now().strftime("%Y-%m-%d-%H%M%S")
        log_file_name: Path = self.log_path / f"recoverpy-{time}.log"

        self._logger: _Logger = getLogger("main")
        self._logger.setLevel(DEBUG)

        file_handler = FileHandler(log_file_name)
        file_handler.setLevel(DEBUG)

        self._logger.addHandler(file_handler)

    def write(self, log_type: str, text: str):
        if not self.log_enabled:
            return

        if log_type == "debug":
            self._logger.debug(text)
        elif log_type == "info":
            self._logger.info(text)
        elif log_type == "warning":
            self._logger.warning(text)
        elif log_type == "error":
            self._logger.error(text)
        elif log_type == "critical":
            self._logger.critical(text)
