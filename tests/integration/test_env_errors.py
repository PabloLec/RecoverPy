import pytest

from recoverpy import RecoverpyApp


@pytest.mark.asyncio
async def test_not_root(
    mock_not_root, mock_linux, mock_valid_version
):
    async with RecoverpyApp().run_test() as p:
        await p.pause()

        assert p.app is not None
        assert p.app.screen.name == "root-error-modal"

        await p.click("#ok-button")
        await p.pause()

        assert p.app.screen.name == "params"


@pytest.mark.asyncio
async def test_invalid_python_version(
    mock_root, mock_linux, mock_invalid_version
):
    async with RecoverpyApp().run_test() as p:
        await p.pause()

        assert p.app is not None
        assert p.app.screen.name == "version-error-modal"


@pytest.mark.asyncio
async def test_not_linux(
    mock_root, mock_not_linux, mock_valid_version
):
    async with RecoverpyApp().run_test() as p:
        await p.pause()

        assert p.app is not None
        assert p.app.screen.name == "linux-error-modal"

        await p.click("#ok-button")
        await p.pause()

        assert p.app.screen.name == "params", "params"


@pytest.mark.asyncio
async def test_multiple_errors(
    mock_not_root,
    mock_not_linux,
    mock_valid_version,
):
    async with RecoverpyApp().run_test() as p:
        await p.pause()

        assert p.app is not None

        for _ in range(2):
            assert "error" in p.app.screen.name
            await p.click("#ok-button")
            await p.pause()

        assert p.app.screen.name == "params"
