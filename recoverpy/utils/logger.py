from logging import Logger, getLogger, FileHandler, DEBUG
from datetime import datetime


class Logger:
    """Logging wrapper object"""

    def __init__(self):
        self.log_path: str = None
        self.log_enabled: bool = False
        self._logger = None

    def start_logging(self):
        time = datetime.now().strftime("%Y-%m-%d-%H%M%S")
        log_file_name = f"{self.log_path}recoverpy-{time}.log"

        self._logger: Logger = getLogger("main")
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


LOGGER = Logger()
