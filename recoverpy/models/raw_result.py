from dataclasses import dataclass

from magika.types import MagikaResult


@dataclass
class RawResult:
    line: str
    identity: MagikaResult
