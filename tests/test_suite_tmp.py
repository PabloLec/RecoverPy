import recoverpy

import py_cui

import pytest

from queue import Queue


@pytest.fixture
def PARAMETERS_MENU():
    view = recoverpy.view_parameters.ParametersView.__new__(recoverpy.view_parameters.ParametersView)
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
def SEARCH_MENU():
    view = recoverpy.view_search.SearchView.__new__(recoverpy.view_search.SearchView)
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
def BLOCK_MENU():
    view = recoverpy.view_results.ResultsView.__new__(recoverpy.view_results.ResultsView)
    view.master = py_cui.PyCUI(10, 10)
    view.partition = "/dev/sda1"
    view.saved_blocks_dict = {}
    view.current_block = 5

    return view


def test_partitions_parsing(PARAMETERS_MENU):
    partitions_dict = PARAMETERS_MENU.format_partitions_list()
    expected_format = {
        "sda1": {"FSTYPE": "ext4", "IS_MOUNTED": True, "MOUNT_POINT": "/media/disk1"},
        "sdb1": {"FSTYPE": "ext4", "IS_MOUNTED": True, "MOUNT_POINT": "/media/disk2"},
        "mmcblk0p1": {"FSTYPE": "vfat", "IS_MOUNTED": True, "MOUNT_POINT": "/boot/firmware"},
        "mmcblk0p2": {"FSTYPE": "ext4", "IS_MOUNTED": True, "MOUNT_POINT": "/"},
        "system-root": {"FSTYPE": "btrfs", "IS_MOUNTED": True, "MOUNT_POINT": "/test"},
        "vdb": {"FSTYPE": "LVM2_member", "IS_MOUNTED": False, "MOUNT_POINT": None},
        "vda2": {"FSTYPE": "LVM2_member", "IS_MOUNTED": False, "MOUNT_POINT": None},
    }
    assert partitions_dict == expected_format


def test_parameters_ui(PARAMETERS_MENU):
    PARAMETERS_MENU.create_ui_content()
    instance_dir = dir(PARAMETERS_MENU)

    assert "partitions_list_scroll_menu" in instance_dir
    assert "string_text_box" in instance_dir
    assert "start_search_button" in instance_dir


def test_partitions_list_population(PARAMETERS_MENU):
    PARAMETERS_MENU.partitions_dict = PARAMETERS_MENU.format_partitions_list()
    PARAMETERS_MENU.create_ui_content()

    PARAMETERS_MENU.add_partitions_to_list()
    expected_item_list = [
        "Name: sda1  -  Type: ext4  -  Mounted at: /media/disk1",
        "Name: sdb1  -  Type: ext4  -  Mounted at: /media/disk2",
        "Name: mmcblk0p1  -  Type: vfat  -  Mounted at: /boot/firmware",
        "Name: mmcblk0p2  -  Type: ext4  -  Mounted at: /",
        "Name: system-root  -  Type: btrfs  -  Mounted at: /test",
        "Name: vdb  -  Type: LVM2_member",
        "Name: vda2  -  Type: LVM2_member",
    ]
    current_item_list = PARAMETERS_MENU.partitions_list_scroll_menu.get_item_list()
    assert current_item_list == expected_item_list


def test_partition_selection(PARAMETERS_MENU):
    PARAMETERS_MENU.partitions_dict = PARAMETERS_MENU.format_partitions_list()
    PARAMETERS_MENU.create_ui_content()

    PARAMETERS_MENU.add_partitions_to_list()

    PARAMETERS_MENU.partitions_list_scroll_menu.set_selected_item_index(0)
    item_0 = "Name: sda1  -  Type: ext4  -  Mounted at: /media/disk1"
    assert PARAMETERS_MENU.partitions_list_scroll_menu.get() == item_0

    PARAMETERS_MENU.select_partition()
    assert PARAMETERS_MENU.partition_to_search == "/dev/sda1"

    PARAMETERS_MENU.partitions_list_scroll_menu.set_selected_item_index(4)
    item_4 = "Name: system-root  -  Type: btrfs  -  Mounted at: /test"
    assert PARAMETERS_MENU.partitions_list_scroll_menu.get() == item_4

    PARAMETERS_MENU.select_partition()
    assert PARAMETERS_MENU.partition_to_search == "/dev/system-root"


def test_search_ui(SEARCH_MENU):
    SEARCH_MENU.create_ui_content()
    instance_dir = dir(SEARCH_MENU)

    assert "search_results_scroll_menu" in instance_dir
    assert "result_content_box" in instance_dir
    assert "previous_button" in instance_dir
    assert "next_button" in instance_dir
    assert "save_file_button" in instance_dir
    assert "exit_button" in instance_dir


def test_result_queue(SEARCH_MENU):
    new_results = SEARCH_MENU.yield_new_results()

    lorem_results = [
        "- 1000: Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod",
        "- 2000: Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod",
        "- 3000: Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod",
    ]
    assert new_results == lorem_results
    assert SEARCH_MENU.result_index == 3

    SEARCH_MENU.queue_object.put("TEST 1")
    new_results = SEARCH_MENU.yield_new_results()

    assert new_results == ["TEST 1"]
    assert SEARCH_MENU.result_index == 4

    SEARCH_MENU.queue_object.put("TEST 2")
    SEARCH_MENU.queue_object.put("TEST 3")
    new_results = SEARCH_MENU.yield_new_results()

    assert new_results == ["TEST 2", "TEST 3"]
    assert SEARCH_MENU.result_index == 6


def test_result_list_population(SEARCH_MENU):
    SEARCH_MENU.create_ui_content()

    new_results = SEARCH_MENU.yield_new_results()
    SEARCH_MENU.add_results_to_list(new_results=new_results)

    item_list = SEARCH_MENU.search_results_scroll_menu.get_item_list()
    expected = [
        "1000: Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmo",
        "2000: Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmo",
        "3000: Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmo",
    ]
    assert item_list == expected


def test_search_title(SEARCH_MENU):
    SEARCH_MENU.create_ui_content()

    SEARCH_MENU.yield_new_results()
    SEARCH_MENU.set_title()

    assert SEARCH_MENU.master._title == "3 results"

    SEARCH_MENU.queue_object.put("TEST 1")
    SEARCH_MENU.yield_new_results()
    SEARCH_MENU.grep_progress = "0.10% ( TEST )"

    SEARCH_MENU.set_title()
    assert SEARCH_MENU.master._title == "0.10% ( TEST ) - 4 results"


def test_block_number_update(SEARCH_MENU):
    SEARCH_MENU.create_ui_content()
    new_results = SEARCH_MENU.yield_new_results()
    SEARCH_MENU.add_results_to_list(new_results=new_results)

    SEARCH_MENU.search_results_scroll_menu.set_selected_item_index(0)
    SEARCH_MENU.update_block_number()
    item_0 = "1000: Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmo"

    assert SEARCH_MENU.current_block == "1"
    assert SEARCH_MENU.search_results_scroll_menu.get() == item_0

    SEARCH_MENU.search_results_scroll_menu.set_selected_item_index(2)
    SEARCH_MENU.update_block_number()
    item_2 = "3000: Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmo"

    assert SEARCH_MENU.current_block == "5"
    assert SEARCH_MENU.search_results_scroll_menu.get() == item_2


def test_save_search_result(SEARCH_MENU, tmp_path):
    SEARCH_MENU.current_block = "NUM"
    SEARCH_MENU.current_result = "TEST CONTENT"
    recoverpy.saver._SAVE_PATH = tmp_path

    SEARCH_MENU.handle_save_view_choice(choice="Save currently displayed block")

    saved_file = recoverpy.saver._LAST_SAVED_FILE

    assert saved_file[-3:] == "NUM"

    with open(saved_file) as f:
        content = f.read()

    expected = "TEST CONTENT"

    assert content == expected


def test_block_ui(BLOCK_MENU):
    BLOCK_MENU.create_ui_content()
    instance_dir = dir(BLOCK_MENU)

    assert "previous_button" in instance_dir
    assert "next_button" in instance_dir
    assert "result_content_box" in instance_dir
    assert "add_result_button" in instance_dir
    assert "save_file_button" in instance_dir
    assert "go_back_button" in instance_dir


def test_add_block_to_file(BLOCK_MENU):
    BLOCK_MENU.create_ui_content()

    for i in range(0, 3):
        BLOCK_MENU.current_block = str(i)
        BLOCK_MENU.current_result = f"TEST {i}"
        BLOCK_MENU.add_block_to_file()

    expected = {"0": "TEST 0", "1": "TEST 1", "2": "TEST 2"}

    assert BLOCK_MENU.saved_blocks_dict == expected


def test_save_multiple_blocks(BLOCK_MENU, tmp_path):
    recoverpy.saver._SAVE_PATH = tmp_path

    for i in range(0, 3):
        BLOCK_MENU.current_block = str(i)
        BLOCK_MENU.current_result = f"TEST {i}"
        BLOCK_MENU.add_block_to_file()

    BLOCK_MENU.save_file()

    saved_file = recoverpy.saver._LAST_SAVED_FILE

    with open(saved_file) as f:
        content = f.read()

    expected = "TEST 0\nTEST 1\nTEST 2\n"

    assert content == expected
