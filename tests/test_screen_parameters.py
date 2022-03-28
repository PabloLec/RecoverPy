def test_parameters_ui(PARAMETERS_SCREEN):
    instance_dir = dir(PARAMETERS_SCREEN)

    assert "partitions_list_scroll_menu" in instance_dir
    assert "string_text_box" in instance_dir
    assert "confirm_search_button" in instance_dir


def test_partitions_parsing(PARAMETERS_SCREEN):
    expected_format = {
        "sda1": {"FSTYPE": "ext4", "IS_MOUNTED": True, "MOUNT_POINT": "/media/disk1"},
        "sdb1": {"FSTYPE": "ntfs", "IS_MOUNTED": True, "MOUNT_POINT": "/media/disk2"},
        "mmcblk0p1": {"FSTYPE": "vfat", "IS_MOUNTED": False, "MOUNT_POINT": None},
        "nvme0n1p1": {"FSTYPE": "ext4", "IS_MOUNTED": True, "MOUNT_POINT": "/"},
        "system-root": {"FSTYPE": "btrfs", "IS_MOUNTED": True, "MOUNT_POINT": "/test"},
        "vdb": {"FSTYPE": "LVM2_member", "IS_MOUNTED": False, "MOUNT_POINT": None},
        "vda2": {"FSTYPE": "LVM2_member", "IS_MOUNTED": False, "MOUNT_POINT": None},
    }

    assert PARAMETERS_SCREEN.partitions_dict == expected_format


def test_partitions_list_population(PARAMETERS_SCREEN):
    expected_item_list = [
        "Name: sda1  -  Type: ext4  -  Mounted at: /media/disk1",
        "Name: sdb1  -  Type: ntfs  -  Mounted at: /media/disk2",
        "Name: mmcblk0p1  -  Type: vfat",
        "Name: nvme0n1p1  -  Type: ext4  -  Mounted at: /",
        "Name: system-root  -  Type: btrfs  -  Mounted at: /test",
        "Name: vdb  -  Type: LVM2_member",
        "Name: vda2  -  Type: LVM2_member",
    ]
    current_item_list = PARAMETERS_SCREEN.partitions_list_scroll_menu.get_item_list()

    assert current_item_list == expected_item_list


def test_partition_selection(PARAMETERS_SCREEN):
    PARAMETERS_SCREEN.partitions_list_scroll_menu.set_selected_item_index(0)
    item_0 = "Name: sda1  -  Type: ext4  -  Mounted at: /media/disk1"
    assert PARAMETERS_SCREEN.partitions_list_scroll_menu.get() == item_0

    PARAMETERS_SCREEN.select_partition()
    assert PARAMETERS_SCREEN.partition_to_search == "/dev/sda1"

    PARAMETERS_SCREEN.partitions_list_scroll_menu.set_selected_item_index(4)
    item_4 = "Name: system-root  -  Type: btrfs  -  Mounted at: /test"
    assert PARAMETERS_SCREEN.partitions_list_scroll_menu.get() == item_4

    PARAMETERS_SCREEN.select_partition()
    assert PARAMETERS_SCREEN.partition_to_search == "/dev/system-root"
