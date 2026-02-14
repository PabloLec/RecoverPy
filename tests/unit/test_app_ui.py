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
        assert any(binding.key == "question_mark" for binding in pilot.app.BINDINGS)


@pytest.mark.asyncio
async def test_question_mark_opens_keyboard_help_modal(session_mocker) -> None:
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
        await pilot.app.action_show_keyboard_help()
        await pilot.pause()

        assert pilot.app.screen.name == "keyboard-help-modal"
        await pilot.click("#ok-button")
        await pilot.pause()
        assert pilot.app.screen.name == "params"


@pytest.mark.asyncio
async def test_question_mark_is_idempotent_when_help_modal_is_open(session_mocker) -> None:
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
        await pilot.app.action_show_keyboard_help()
        await pilot.pause()
        assert pilot.app.screen.name == "keyboard-help-modal"

        await pilot.app.action_show_keyboard_help()
        await pilot.pause()
        assert pilot.app.screen.name == "keyboard-help-modal"
