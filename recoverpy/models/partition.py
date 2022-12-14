from dataclasses import dataclass


@dataclass
class Partition:
    name: str
    fs_type: str
    is_mounted: bool
    mount_point: str

    def get_full_name(self):
        return f"/dev/{self.name}"
