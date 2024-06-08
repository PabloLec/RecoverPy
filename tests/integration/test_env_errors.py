import pytest

from recoverpy import RecoverpyApp
from tests.integration.helper import assert_with_timeout


@pytest.mark.asyncio
async def test_not_root(
    mock_not_root, mock_linux, mock_valid_version, mock_dependencies_installed
):
    async with RecoverpyApp().run_test() as p:
        assert p.app is not None
        await assert_with_timeout(
            lambda: p.app.screen.name == "root-error-modal",
            "root-error-modal",
            p.app.screen.name,
        )
        await p.click("#ok-button")
        await assert_with_timeout(
            lambda: p.app.screen.name == "params", "params", p.app.screen.name
        )


@pytest.mark.asyncio
async def test_invalid_python_version(
    mock_root, mock_linux, mock_invalid_version, mock_dependencies_installed
):
    async with RecoverpyApp().run_test() as p:
        assert p.app is not None
        await assert_with_timeout(
            lambda: p.app.screen.name == "version-error-modal",
            "version-error-modal",
            p.app.screen.name,
        )


@pytest.mark.asyncio
async def test_not_linux(
    mock_root, mock_not_linux, mock_valid_version, mock_dependencies_installed
):
    async with RecoverpyApp().run_test() as p:
        assert p.app is not None
        await assert_with_timeout(
            lambda: p.app.screen.name == "linux-error-modal",
            "linux-error-modal",
            p.app.screen.name,
        )
        await p.click("#ok-button")
        await assert_with_timeout(
            lambda: p.app.screen.name == "params", "params", p.app.screen.name
        )


@pytest.mark.asyncio
async def test_dependencies_not_installed(
    mock_root, mock_linux, mock_valid_version, mock_dependencies_not_installed
):
    async with RecoverpyApp().run_test() as p:
        assert p.app is not None
        await assert_with_timeout(
            lambda: p.app.screen.name == "dependencies-error-modal",
            "dependencies-error-modal",
            p.app.screen.name,
        )
        await p.click("#ok-button")
        await assert_with_timeout(
            lambda: p.app.screen.name == "params", "params", p.app.screen.name
        )


@pytest.mark.asyncio
async def test_multiple_errors(
    mock_not_root,
    mock_not_linux,
    mock_valid_version,
    mock_dependencies_not_installed,
):
    async with RecoverpyApp().run_test() as p:
        assert p.app is not None
        for _ in range(3):
            await assert_with_timeout(
                lambda: "error" in p.app.screen.name, "error", p.app.screen.name
            )
            await p.click("#ok-button")
        await assert_with_timeout(
            lambda: p.app.screen.name == "params", "params", p.app.screen.name
        )
