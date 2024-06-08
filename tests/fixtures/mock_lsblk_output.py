MOCK_LSBLK_OUTPUT = """loop1 loop squashfs /snap/core18/2284
loop0 loop squashfs /snap/chromium/2238
sda disk
sda1 part ext4 /media/disk1
sdb disk
sdb1 part ntfs /media/disk2
mmcblk0 disk
mmcblk0p1 part vfat
nvme0n1 disk
nvme0n1p1 part ext4 /
system-root lvm btrfs /test
vdb disk LVM2_member
vda2 part LVM2_member"""

VISIBLE_PARTITION_COUNT = 7
UNFILTERED_PARTITION_COUNT = 9
