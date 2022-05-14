from subprocess import PIPE, Popen

MOCK_GREP_OUTPUT = """1000: Lorem ipsum dolor sit amet, test consectetur adipiscing elit, sed do
2000: Lorem ipsum dolor sit amet, test consectetur adipiscing elit, sed do
3000: Lorem ipsum dolor sit amet, test consectetur adipiscing elit, sed do """


def create_grep_process(self, searched_string: str, partition: str) -> Popen:
    return Popen(
        ["echo", MOCK_GREP_OUTPUT],
        stdin=None,
        stdout=PIPE,
        stderr=None,
    )
