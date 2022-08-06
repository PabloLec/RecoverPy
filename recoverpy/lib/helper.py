from os import geteuid
from re import findall
from subprocess import DEVNULL, call, check_output

from py_cui import PyCUI

from recoverpy.lib.logger import Logger

_IGNORED_PARTITIONS_TYPES: tuple = (" loop ", "swap")


def is_user_root(window: PyCUI) -> bool:
    if geteuid() == 0:
        Logger().write("info", "User is root")
        return True

    window.show_error_popup("Not root :(", "You have to be root or use sudo.")
    Logger().write("warning", "User is not root")
    return False


def get_partitions() -> dict:
    lsblk_output: str = lsblk()
    return format_lsblk_output(lsblk_output)


def lsblk() -> str:
    return check_output(
        ["lsblk", "-r", "-n", "-o", "NAME,TYPE,FSTYPE,MOUNTPOINT"],
        encoding="utf-8",
    )


def format_lsblk_output(lsblk_output: str) -> dict:
    partitions_dict = {}

    for line in lsblk_output.splitlines():
        if any(word in line for word in _IGNORED_PARTITIONS_TYPES):
            continue

        values = line.strip().split()

        if len(values) < 3:
            # Ignore if no FSTYPE detected
            continue

        if len(values) < 4:
            is_mounted = False
            mount_point = None
        else:
            is_mounted = True
            mount_point = values[3]

        partitions_dict[values[0]] = {
            "FSTYPE": values[2],
            "IS_MOUNTED": is_mounted,
            "MOUNT_POINT": mount_point,
        }

    return partitions_dict


def is_dependency_installed(command: str) -> bool:
    return call(["which", command], stdout=DEVNULL) == 0


def decode_result(result: bytes) -> str:
    return result.decode("utf-8", errors="ignore")


def get_printable(result: str) -> str:
    return "".join(([c for c in result.replace("\n", " ") if c.isprintable()]))


def get_block_size(partition: str) -> int:
    return int(
        check_output(
            ["blockdev", "--getbsz", partition],
            encoding="utf-8",
        )
    )


def get_inode(string: str) -> str:
    match = findall(r"^(\d+):", string)
    return match[0] if len(match) >= 1 else None
