MOCK_BLOCK_DEVICES = [
    "loop1",
    "loop0",
    "sda",
    "sda1",
    "sdb",
    "sdb1",
    "mmcblk0",
    "mmcblk0p1",
    "nvme0n1",
    "nvme0n1p1",
    "system-root",
    "vdb",
    "vda2",
]

MOCK_DEVICE_TYPES = {
    "loop1": "loop",
    "loop0": "loop",
    "sda": "disk",
    "sda1": "partition",
    "sdb": "disk",
    "sdb1": "partition",
    "mmcblk0": "disk",
    "mmcblk0p1": "partition",
    "nvme0n1": "disk",
    "nvme0n1p1": "partition",
    "system-root": "lvm",
    "vdb": "lvm",
    "vda2": "partition",
}

MOCK_PROC_PARTITION_SIZES = {
    "loop1": 1000,
    "loop0": 1000,
    "sda": 1000000,
    "sda1": 100000,
    "sdb": 1000000,
    "sdb1": 100000,
    "mmcblk0": 2000000,
    "mmcblk0p1": 500000,
    "nvme0n1": 4000000,
    "nvme0n1p1": 2000000,
    "system-root": 1500000,
    "vdb": 1500000,
    "vda2": 1500000,
}

MOCK_PROC_MOUNTS = {
    "/dev/loop1": [("/snap/core18/2284", "squashfs")],
    "/dev/loop0": [("/snap/chromium/2238", "squashfs")],
    "/dev/sda1": [("/media/disk1", "ext4")],
    "/dev/sdb1": [("/media/disk2", "ntfs")],
    "/dev/nvme0n1p1": [("/", "ext4")],
    "/dev/system-root": [("/test", "btrfs")],
}

VISIBLE_PARTITION_COUNT = 7
UNFILTERED_PARTITION_COUNT = 9


def mock_read_device_type(name: str) -> str:
    return MOCK_DEVICE_TYPES[name]
