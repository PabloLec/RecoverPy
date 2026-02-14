from dataclasses import dataclass
from typing import Optional


@dataclass
class Partition:
    name: str
    fs_type: str
    is_mounted: bool
    mount_point: Optional[str]
    size_bytes: int = 0
    device_type: str = "unknown"
    device_path: Optional[str] = None

    def get_full_name(self) -> str:
        return self.device_path or f"/dev/{self.name}"
