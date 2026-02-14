"""Persistence helper for user-selected recovered blocks."""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from recoverpy.log.logger import log


class Saver:
    def __init__(self) -> None:
        self.save_path: Path = Path.cwd()
        self.last_saved_file: Optional[Path] = None
        self._results: Dict[int, str] = {}

    def add_result(self, inode: int, result: str) -> None:
        self._results[inode] = result
        log.info(f"Saver - Added result for inode {inode}, {len(self._results)} total")

    def reset_results(self) -> None:
        self._results.clear()
        log.info("Saver - Results reset")

    def save_results(self) -> None:
        ordered_blocks: List[str] = [
            self._results[key] for key in sorted(self._results)
        ]
        final_output: str = "\n".join(ordered_blocks)

        self._save_result_string(final_output)
        self.reset_results()

    def set_save_path(self, path: str) -> None:
        self.save_path = Path(path)
        log.info(f"Saver - Save path set to {self.save_path}")

    def get_blocks_to_save_count(self) -> int:
        return len(self._results)

    def _save_result_string(self, result: str) -> None:
        if not self.save_path:
            return

        timestamp = datetime.now().strftime("recoverpy-save-%Y-%m-%d-%H%M%S")
        file_name: Path = self.save_path / timestamp

        self._write_to_file(file_name, result)
        log.info(f"Saver - Saved result to {file_name}")

    def _write_to_file(self, file_name: Path, content: str) -> None:
        with open(file_name, "w") as save_file:
            save_file.write(content)

        self.last_saved_file = file_name
