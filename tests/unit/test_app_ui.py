from unittest.mock import MagicMock

import pytest
from textual.widgets import Footer

from recoverpy import RecoverpyApp


@pytest.mark.asyncio
async def test_app_displays_footer_with_bindings(session_mocker) -> None:
    session_mocker.patch(
        "recoverpy.lib.env_check._is_user_root",
        MagicMock(return_value=True),
    )
    session_mocker.patch(
        "recoverpy.lib.env_check._are_system_dependencies_installed",
        MagicMock(return_value=True),
    )
    session_mocker.patch(
        "recoverpy.lib.env_check._is_linux",
        MagicMock(return_value=True),
    )

    async with RecoverpyApp().run_test() as pilot:
        await pilot.pause()
        assert isinstance(pilot.app.query_one(Footer), Footer)
