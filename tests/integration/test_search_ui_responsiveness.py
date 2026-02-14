from pathlib import Path
from time import sleep
from unittest.mock import MagicMock

import pytest

from recoverpy import RecoverpyApp
from recoverpy.lib.storage.block_device_metadata import DeviceInfo
from recoverpy.lib.search.binary_scanner import ScanHit
from recoverpy.ui.screens.screen_params import ParamsScreen
from tests.conftest import TEST_BLOCK_SIZE


def _slow_hits(*args, **kwargs):
    for i in range(60):
        sleep(0.03)
        yield ScanHit(
            match_offset=(i + 1) * 4096,
            preview=b"Lorem ipsum responsiveness test",
        )


@pytest.mark.asyncio
async def test_ui_remains_responsive_during_scan(mocker, tmp_path: Path):
    mocker.patch(
        "recoverpy.lib.env_check._is_user_root",
        MagicMock(return_value=True),
    )
    mocker.patch(
        "recoverpy.lib.env_check._is_linux",
        MagicMock(return_value=True),
    )
    mocker.patch(
        "recoverpy.lib.search.search_engine.iter_scan_hits",
        side_effect=_slow_hits,
    )
    mocker.patch(
        "recoverpy.lib.search.search_engine.get_device_info",
        return_value=DeviceInfo(
            size_bytes=1024 * 1024,
            logical_sector_size=TEST_BLOCK_SIZE,
            physical_sector_size=TEST_BLOCK_SIZE,
            read_only=False,
            is_block_device=True,
        ),
    )

    async with RecoverpyApp().run_test() as pilot:
        await pilot.pause()
        pilot.app.post_message(ParamsScreen.Continue("TEST", "/dev/sdb1"))
        await pilot.pause()

        assert pilot.app.screen.name == "search"

        # If the UI loop is blocked by the scan, this modal can't open while scanning.
        await pilot.press("?")
        await pilot.pause()
        assert pilot.app.screen.name == "keyboard-help-modal"

        await pilot.click("#ok-button")
        await pilot.pause()
        assert pilot.app.screen.name == "search"
