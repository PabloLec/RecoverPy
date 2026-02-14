from pathlib import Path
from types import SimpleNamespace

import pytest

from recoverpy.ui.screens.screen_path_edit import PathEditScreen


@pytest.mark.asyncio
async def test_directory_selected_updates_current_selection() -> None:
    screen = PathEditScreen()
    event = SimpleNamespace(path=Path("/tmp"), stop=lambda: None)

    await screen.on_directory_tree_directory_selected(event)  # type: ignore[arg-type]

    assert screen._selected_dir == "/tmp"
    assert "Selected directory: /tmp" == str(screen._selected_dir_label.content)


@pytest.mark.asyncio
async def test_file_selected_keeps_directory_only_and_notifies(session_mocker) -> None:
    screen = PathEditScreen()
    notify_mock = session_mocker.patch.object(screen, "notify")
    event = SimpleNamespace(path=Path("/tmp/file.txt"), stop=lambda: None)

    await screen.on_directory_tree_file_selected(event)  # type: ignore[arg-type]

    assert screen._selected_dir == "/"
    notify_mock.assert_called_once_with(
        "Only directories can be selected.", severity="warning"
    )
