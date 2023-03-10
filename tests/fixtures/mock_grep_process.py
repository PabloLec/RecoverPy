from pathlib import Path
from subprocess import PIPE, Popen
from tempfile import gettempdir

MOCK_GREP_OUTPUT = """4096: Lorem ipsum dolor sit amet, test consectetur adipiscing elit, sed do
8192: Lorem ipsum dolor sit amet, test consectetur adipiscing elit, sed da
12288: Lorem ipsum dolor sit amet, test consectetur adipiscing elit, sed du"""


def mock_start_grep_process(*args, **kwargs) -> Popen:
    grep_output_file = Path(gettempdir()) / "grep_output.txt"
    grep_output_file.write_text(MOCK_GREP_OUTPUT)
    return Popen(
        ["cat", grep_output_file, ";", "sleep", "infinity"],
        stdin=None,
        stdout=PIPE,
        stderr=None,
    )
