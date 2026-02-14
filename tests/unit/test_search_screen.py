from unittest.mock import MagicMock

import pytest

from recoverpy import RecoverpyApp
from recoverpy.lib.device_io import DeviceIOError
from recoverpy.ui.screens.screen_search import SearchScreen


def test_check_action_disables_open_when_button_disabled() -> None:
    screen = SearchScreen()
    screen._open_button = type("FakeButton", (), {"disabled": True})()  # type: ignore[assignment]

    assert screen.check_action("open_result", ()) is None


@pytest.mark.asyncio
async def test_search_start_error_returns_to_params(session_mocker) -> None:
    session_mocker.patch(
        "recoverpy.lib.env_check._is_user_root",
        MagicMock(return_value=True),
    )
    session_mocker.patch(
        "recoverpy.lib.env_check._is_linux",
        MagicMock(return_value=True),
    )
    session_mocker.patch(
        "recoverpy.ui.screens.screen_search.SearchEngine",
        side_effect=DeviceIOError(
            "Cannot open /dev/sdb1", "Permission denied: cannot open /dev/sdb1 (run as root)."
        ),
    )

    async with RecoverpyApp().run_test() as pilot:
        await pilot.pause()
        await pilot.click("#sdb1")
        for char in "TEST":
            await pilot.press(char)
        await pilot.press("enter")
        await pilot.pause()

        assert pilot.app.screen.name == "params"
