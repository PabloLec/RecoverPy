from pathlib import Path
from typing import List


def get_css() -> List[Path]:
    return list(Path(__file__).resolve().parent.glob("*.css"))
