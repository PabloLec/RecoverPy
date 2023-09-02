from subprocess import PIPE, Popen

GREP_RESULT_COUNT = 3

_MOCK_GREP_OUTPUT = """4096: Lorem ipsum dolor sit amet, test consectetur adipiscing elit, sed do
8192: Lorem ipsum dolor sit amet, test consectetur adipiscing elit, sed da
12288: Lorem ipsum dolor sit amet, test consectetur adipiscing elit, sed du"""


def mock_start_grep_process(*args, **kwargs) -> Popen:
    return Popen(["printf", _MOCK_GREP_OUTPUT], stdin=None, stdout=PIPE, stderr=None)
