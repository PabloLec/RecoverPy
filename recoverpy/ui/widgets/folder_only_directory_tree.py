from pathlib import Path
from typing import Iterable

from textual.widgets import DirectoryTree


class FolderOnlyDirectoryTree(DirectoryTree):
    """DirectoryTree wrapper that only shows directories."""

    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        return [path for path in paths if path.is_dir()]
