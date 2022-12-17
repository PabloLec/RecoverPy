import pathlib
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict


class Saver:
    """Encapsulates all result saving related methods."""

    def __init__(self):
        self.save_path: Path = Path().absolute()
        self.last_saved_file: Optional[Path] = None
        self._results: Dict[int, str] = {}

    def add(self, inode: int, result: str):
        self._results[inode] = result

    def reset(self):
        self._results = {}

    def save(self):
        ordered_blocks: list = [self._results[num] for num in sorted(self._results.keys())]
        final_output: str = "\n".join(ordered_blocks)

        self._save_result_string(final_output)

    def update_save_path(self, path: str):
        self.save_path = pathlib.Path(path)

    def _save_result_string(self, result: str):
        if self.save_path is None:
            return
        time_format: str = datetime.now().strftime("recoverpy-save-%Y-%m-%d-%H%M%S")
        file_name: Path = self.save_path / time_format

        self._write_to_file(file_name=file_name, content=result)

    def _write_to_file(self, file_name: Path, content: str):
        with open(file_name, "w") as save_file:
            save_file.write(content)

        self.last_saved_file = file_name

