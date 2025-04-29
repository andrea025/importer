from dataclasses import dataclass, field
from typing import List

@dataclass
class Adversary:
    adversary_id: str
    name: str
    description: str
    atomic_ordering: List[str] = field(default_factory=list)
