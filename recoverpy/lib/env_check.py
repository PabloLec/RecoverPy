from os import geteuid
from platform import system
from sys import exit, version_info

from textual.app import App

from recoverpy.lib.helper import is_dependency_installed
from recoverpy.log.logger import log
from recoverpy.ui.screens.modal import install_and_push_modal

_root_error_message = "The current user is not root, the search is likely to not work. Run this app as root or use sudo."
_version_error_message = (
    "The current Python version is not supported. Please use Python 3.8 or higher."
)
_linux_error_message = (
    "Your system may not be Linux-based, the application might not work correctly."
)
_dependencies_error_message = "Some dependencies are not installed. Please install grep, dd, lsblk and blockdev and restart the application."


async def verify_app_environment(app: App[None]) -> None:
    if not _is_version_supported():
        log.error("app - Python version not supported")
        await install_and_push_modal(
            app, "version-error-modal", _version_error_message, exit
        )
    if not _is_linux():
        log.warning("app - System is not Linux-based")
        await install_and_push_modal(app, "linux-error-modal", _linux_error_message)
    if not _is_user_root():
        log.warning("app - User is not root")
        await install_and_push_modal(app, "root-error-modal", _root_error_message)
    if not _are_system_dependencies_installed():
        log.warning("app - Some dependencies are not installed")
        await install_and_push_modal(
            app, "dependencies-error-modal", _dependencies_error_message
        )


def _is_user_root() -> bool:
    return geteuid() == 0


def _is_version_supported() -> bool:
    return version_info >= (3, 8)


def _is_linux() -> bool:
    return "linux" in system().lower()


def _are_system_dependencies_installed() -> bool:
    for dependency in ("grep", "dd", "lsblk", "blockdev"):
        if not is_dependency_installed(dependency):
            return False
    return True
