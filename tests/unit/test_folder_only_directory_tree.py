from pathlib import Path

from recoverpy.ui.widgets.folder_only_directory_tree import \
    FolderOnlyDirectoryTree


def test_filter_paths_keeps_only_directories(tmp_path: Path) -> None:
    visible_dir = tmp_path / "visible-dir"
    visible_dir.mkdir()
    hidden_file = tmp_path / "file.txt"
    hidden_file.write_text("x")

    tree = object.__new__(FolderOnlyDirectoryTree)
    filtered = list(tree.filter_paths([visible_dir, hidden_file]))

    assert filtered == [visible_dir]


def test_filter_paths_is_reiterable(tmp_path: Path) -> None:
    visible_dir = tmp_path / "visible-dir"
    visible_dir.mkdir()
    hidden_file = tmp_path / "file.txt"
    hidden_file.write_text("x")

    tree = object.__new__(FolderOnlyDirectoryTree)
    filtered = tree.filter_paths([visible_dir, hidden_file])

    assert list(filtered) == [visible_dir]
    assert list(filtered) == [visible_dir]
