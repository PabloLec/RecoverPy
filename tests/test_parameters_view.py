import recoverpy


def test_partitions_parsing(PARAMETERS_VIEW):
    partitions_dict = recoverpy.utils.helper.format_partitions_list(
        window=PARAMETERS_VIEW.master, raw_lsblk=PARAMETERS_VIEW.partitions_list
    )
    expected_format = {
        "sda1": {"FSTYPE": "ext4", "IS_MOUNTED": True, "MOUNT_POINT": "/media/disk1"},
        "sdb1": {"FSTYPE": "ext4", "IS_MOUNTED": True, "MOUNT_POINT": "/media/disk2"},
        "mmcblk0p1": {
            "FSTYPE": "vfat",
            "IS_MOUNTED": True,
            "MOUNT_POINT": "/boot/firmware",
        },
        "mmcblk0p2": {"FSTYPE": "ext4", "IS_MOUNTED": True, "MOUNT_POINT": "/"},
        "system-root": {"FSTYPE": "btrfs", "IS_MOUNTED": True, "MOUNT_POINT": "/test"},
        "vdb": {"FSTYPE": "LVM2_member", "IS_MOUNTED": False, "MOUNT_POINT": None},
        "vda2": {"FSTYPE": "LVM2_member", "IS_MOUNTED": False, "MOUNT_POINT": None},
    }
    assert partitions_dict == expected_format


def test_parameters_ui(PARAMETERS_VIEW):
    PARAMETERS_VIEW.create_ui_content()
    instance_dir = dir(PARAMETERS_VIEW)

    assert "partitions_list_scroll_menu" in instance_dir
    assert "string_text_box" in instance_dir
    assert "confirm_search_button" in instance_dir


def test_partitions_list_population(PARAMETERS_VIEW):
    PARAMETERS_VIEW.partitions_dict = recoverpy.utils.helper.format_partitions_list(
        window=PARAMETERS_VIEW.master, raw_lsblk=PARAMETERS_VIEW.partitions_list
    )
    PARAMETERS_VIEW.create_ui_content()

    PARAMETERS_VIEW.add_partitions_to_list()
    expected_item_list = [
        "Name: sda1  -  Type: ext4  -  Mounted at: /media/disk1",
        "Name: sdb1  -  Type: ext4  -  Mounted at: /media/disk2",
        "Name: mmcblk0p1  -  Type: vfat  -  Mounted at: /boot/firmware",
        "Name: mmcblk0p2  -  Type: ext4  -  Mounted at: /",
        "Name: system-root  -  Type: btrfs  -  Mounted at: /test",
        "Name: vdb  -  Type: LVM2_member",
        "Name: vda2  -  Type: LVM2_member",
    ]
    current_item_list = PARAMETERS_VIEW.partitions_list_scroll_menu.get_item_list()
    assert current_item_list == expected_item_list


def test_partition_selection(PARAMETERS_VIEW):
    PARAMETERS_VIEW.partitions_dict = recoverpy.utils.helper.format_partitions_list(
        window=PARAMETERS_VIEW.master, raw_lsblk=PARAMETERS_VIEW.partitions_list
    )
    PARAMETERS_VIEW.create_ui_content()

    PARAMETERS_VIEW.add_partitions_to_list()

    PARAMETERS_VIEW.partitions_list_scroll_menu.set_selected_item_index(0)
    item_0 = "Name: sda1  -  Type: ext4  -  Mounted at: /media/disk1"
    assert PARAMETERS_VIEW.partitions_list_scroll_menu.get() == item_0

    PARAMETERS_VIEW.select_partition()
    assert PARAMETERS_VIEW.partition_to_search == "/dev/sda1"

    PARAMETERS_VIEW.partitions_list_scroll_menu.set_selected_item_index(4)
    item_4 = "Name: system-root  -  Type: btrfs  -  Mounted at: /test"
    assert PARAMETERS_VIEW.partitions_list_scroll_menu.get() == item_4

    PARAMETERS_VIEW.select_partition()
    assert PARAMETERS_VIEW.partition_to_search == "/dev/system-root"
