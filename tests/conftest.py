import recoverpy
import py_cui
import pytest

from queue import Queue


@pytest.fixture
def PARAMETERS_VIEW():
    view = recoverpy.views.view_parameters.ParametersView.__new__(recoverpy.views.view_parameters.ParametersView)
    view.master = py_cui.PyCUI(10, 10)

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


@pytest.fixture
def _SEARCH_VIEW():
    view = recoverpy.views.view_search.SearchView.__new__(recoverpy.views.view_search.SearchView)
    view.master = py_cui.PyCUI(10, 10)
    view.queue_object = Queue()
    lorem = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod"
    view.queue_object.put(f"- 1000: {lorem}")
    view.queue_object.put(f"- 2000: {lorem}")
    view.queue_object.put(f"- 3000: {lorem}")
    view.result_index = 0
    view.grep_progress = ""
    view.block_size = 512

    return view


@pytest.fixture
def RESULTS_VIEW():
    view = recoverpy.views.view_results.ResultsView.__new__(recoverpy.views.view_results.ResultsView)
    view.master = py_cui.PyCUI(10, 10)
    view.partition = "/dev/sda1"
    view.saved_blocks_dict = {}
    view.current_block = 5

    return view
