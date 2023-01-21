from pathlib import Path
from typing import List


def get_css() -> List[str]:
    return list(map(str, Path(__file__).resolve().parent.glob("*.css")))
