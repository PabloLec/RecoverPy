import argparse
import logging
from datetime import datetime
from os import path
from tempfile import gettempdir

from recoverpy.log.logger import log
from recoverpy.ui.app import RecoverpyApp


def _set_logger() -> None:
    global log

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true", help="Enable logging")

    args = parser.parse_args()
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    log_file_path = path.join(gettempdir(), f"recoverpy-{timestamp}.log")

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.CRITICAL,
        format="%(asctime)s - %(levelname)s - [%(threadName)s] - %(message)s",
        handlers=[logging.FileHandler(log_file_path)]
        if args.debug
        else [logging.NullHandler()],
    )
    log = logging.getLogger()


def main() -> None:
    _set_logger()
    log.info("Starting Recoverpy app")
    RecoverpyApp().run()


if __name__ == "__main__":
    main()
