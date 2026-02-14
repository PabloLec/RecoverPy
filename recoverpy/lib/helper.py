from re import findall
from subprocess import DEVNULL, call, check_output


def is_dependency_installed(command: str) -> bool:
    return call(["which", command], stdout=DEVNULL) == 0


def decode_result(result: bytes) -> str:
    return result.decode("utf-8", errors="ignore")


def get_printable(result: str) -> str:
    return "".join(([c for c in result.replace("\n", " ") if c.isprintable()]))


def get_block_size(partition: str) -> int:
    return int(
        check_output(
            ["blockdev", "--getbsz", partition],
            encoding="utf-8",
        )
    )


def get_inode(string: str) -> int:
    match = findall(r"^(\d+):", string)
    return int(match[0])
