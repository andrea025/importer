from dataclasses import dataclass, field
from typing import List

@dataclass
class Executor:
    name: str
    platform: str
    command: str
    cleanup: str = ''
    payloads: List[str] = field(default_factory=list)
