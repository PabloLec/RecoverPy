from queue import Queue

import pytest
from py_cui import PyCUI

import recoverpy


@pytest.fixture()
def PARAMETERS_VIEW():
    view = recoverpy.views.view_parameters.ParametersView.__new__(
        recoverpy.views.view_parameters.ParametersView
    )
    view.master = PyCUI(10, 10)

    partitions = [
        ["sda", "disk"],
        ["sda1", "part", "ext4", "/media/disk1"],
        ["sdb", "disk"],
        ["sdb1", "part", "ext4", "/media/disk2"],
        ["mmcblk0", "disk"],
        ["mmcblk0p1", "part", "vfat", "/boot/firmware"],
        ["mmcblk0p2", "part", "ext4", "/"],
        ["system-root", "lvm", "btrfs", "/test"],
        ["vdb", "disk", "LVM2_member"],
        ["vda2", "part", "LVM2_member"],
    ]
    view.partitions_list = partitions

    return view


@pytest.fixture()
def SEARCH_VIEW():
    view = recoverpy.views.view_search.SearchView.__new__(
        recoverpy.views.view_search.SearchView
    )
    view.master = PyCUI(10, 10)
    view.queue_object = Queue()
    lorem = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod"
    view.queue_object.put(f"- 1000: {lorem}")
    view.queue_object.put(f"- 2000: {lorem}")
    view.queue_object.put(f"- 3000: {lorem}")
    view.result_index = 0
    view.grep_progress = ""
    view.block_size = 512
    view.searched_string = "test"
    view.inodes = [512, 1024, 2056]

    return view


@pytest.fixture()
def RESULTS_VIEW():
    view = recoverpy.views.view_results.ResultsView.__new__(
        recoverpy.views.view_results.ResultsView
    )
    view.master = PyCUI(10, 10)
    view.partition = "/dev/sda1"
    view.saved_blocks_dict = {}
    view.current_block = 5

    return view


@pytest.fixture()
def CONFIG_VIEW():
    view = recoverpy.views.view_config.ConfigView.__new__(
        recoverpy.views.view_config.ConfigView
    )
    view.master = PyCUI(10, 10)
    view._log_enabled = True

    return view


@pytest.fixture(scope="session")
def TEST_FILE(tmp_path_factory):
    lorem = "Integer vitae ultrices magna. Nam non cursus odio. In dapibus augue.\n"
    file = tmp_path_factory.mktemp("data") / "file"
    with file.open("w", encoding="utf-8") as f:
        f.write(lorem * 20000 + "TEST STRING" + lorem * 20000)

    return file
