import py_cui

from subprocess import check_output, call
from os import geteuid

from recoverpy import logger as LOGGER


def is_user_root(window: py_cui.PyCUI) -> bool:
    """Checks if user has root privileges.
    The method is simply verifying if EUID == 0.
    It may be problematic in some edge cases. (Some particular OS)
    But, as grep search will not exit quickly, exception handling
    can't be used.

    Args:
        window (py_cui.PyCUI): PyCUI window to display popup.

    Returns:
        bool: User is root
    """

    if geteuid() == 0:
        LOGGER.write("info", "User is root")
        return True

    window.show_error_popup("Not root", "You have to be root or use sudo.")
    LOGGER.write("warning", "User is not root")
    return False


def lsblk() -> list:
    """Uses 'lsblk' utility to generate a list of detected
    system partions."

    Returns:
        list: List of system partitions.
    """

    lsblk_output = check_output(["lsblk", "-r", "-n", "-o", "NAME,TYPE,FSTYPE,MOUNTPOINT"], encoding="utf-8")
    partitions_list_raw = [
        line.strip() for line in lsblk_output.splitlines() if " loop " not in line and "swap" not in line
    ]
    partitions_list_formatted = [line.split(" ") for line in partitions_list_raw]

    LOGGER.write(
        "debug",
        str(partitions_list_formatted),
    )

    return partitions_list_formatted


def format_partitions_list(window: py_cui.PyCUI, raw_lsblk: list) -> dict:
    """Uses lsblk command to find partitions.

    Args:
        window (py_cui.PyCUI): PyCUI window to display popup.
        raw_lsblk (list): Raw lsblk output.

    Returns:
        dict: Found partitions with format :
            {Name: FSTYPE, IS_MOUNTED, MOUNT_POINT}
    """

    # Create dict with relevant infos
    partitions_dict = {}
    for partition in raw_lsblk:
        if len(partition) < 3:
            # Ignore if no FSTYPE detected
            continue

        if len(partition) < 4:
            is_mounted = False
            mount_point = None
        else:
            is_mounted = True
            mount_point = partition[3]

        partitions_dict[partition[0]] = {
            "FSTYPE": partition[2],
            "IS_MOUNTED": is_mounted,
            "MOUNT_POINT": mount_point,
        }

    # Warn the user if no partition found with lsblk
    if len(partitions_dict) == 0:
        LOGGER.write("Error", "No partition found !")
        window.show_error_popup("Error", "No partition found.")
        return None

    LOGGER.write("debug", "Partition list generated using 'lsblk'")
    LOGGER.write(
        "debug",
        f"{str(len(partitions_dict))} partitions found",
    )

    return partitions_dict


def is_progress_installed() -> bool:
    """Verifies if 'progress' tool is installed on current system.

    Returns:
        bool: 'progress' is installed.
    """

    output = call("command -v progress", shell=True)
    if output == 0:
        return True
    else:
        return False
