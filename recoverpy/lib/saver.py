from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class Saver:
    """Encapsulates all result saving related methods."""

    def __init__(self) -> None:
        self.save_path: Path = Path().absolute()
        self.last_saved_file: Optional[Path] = None
        self._results: Dict[int, str] = {}

    def add(self, inode: int, result: str) -> None:
        self._results[inode] = result

    def reset(self) -> None:
        self._results = {}

    def save(self) -> None:
        ordered_blocks: List[str] = [
            self._results[num] for num in sorted(self._results.keys())
        ]
        final_output: str = "\n".join(ordered_blocks)

        self._save_result_string(final_output)
        self.reset()

    def update_save_path(self, path: str) -> None:
        self.save_path = Path(path)

    def get_selected_blocks_count(self) -> int:
        return len(self._results)

    def _save_result_string(self, result: str) -> None:
        if self.save_path is None:
            return
        time_format: str = datetime.now().strftime("recoverpy-save-%Y-%m-%d-%H%M%S")
        file_name: Path = self.save_path / time_format

        self._write_to_file(file_name=file_name, content=result)

    def _write_to_file(self, file_name: Path, content: str) -> None:
        with open(file_name, "w") as save_file:
            save_file.write(content)

        self.last_saved_file = file_name
