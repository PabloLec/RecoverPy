import pytest

from tests.integration.helper import assert_with_timeout


@pytest.mark.asyncio
async def test_not_root(
    pilot, mock_not_root, mock_linux, mock_valid_version, mock_dependencies_installed
):
    async with pilot as p:
        assert p.app is not None
        await assert_with_timeout(lambda: p.app.screen.name == "root-error-modal")


@pytest.mark.asyncio
async def test_invalid_python_version(
    pilot, mock_root, mock_linux, mock_invalid_version, mock_dependencies_installed
):
    async with pilot as p:
        assert p.app is not None
        await assert_with_timeout(lambda: p.app.screen.name == "version-error-modal")


@pytest.mark.asyncio
async def test_not_linux(
    pilot, mock_root, mock_not_linux, mock_valid_version, mock_dependencies_installed
):
    async with pilot as p:
        assert p.app is not None
        await assert_with_timeout(lambda: p.app.screen.name == "linux-error-modal")


@pytest.mark.asyncio
async def test_dependencies_not_installed(
    pilot, mock_root, mock_linux, mock_valid_version, mock_dependencies_not_installed
):
    async with pilot as p:
        assert p.app is not None
        await assert_with_timeout(
            lambda: p.app.screen.name == "dependencies-error-modal"
        )
