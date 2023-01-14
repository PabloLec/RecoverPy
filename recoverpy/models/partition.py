from dataclasses import dataclass
from typing import Optional


@dataclass
class Partition:
    name: str
    fs_type: str
    is_mounted: bool
    mount_point: Optional[str]

    def get_full_name(self):
        return f"/dev/{self.name}"
