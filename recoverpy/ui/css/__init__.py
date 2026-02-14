from pathlib import Path
from typing import List


def get_css() -> List[Path]:
    css_dir = Path(__file__).resolve().parent
    css_files = list(css_dir.glob("*.css"))
    tcss_files = list(css_dir.glob("*.tcss"))
    return sorted(css_files + tcss_files)
