from dataclasses import dataclass, field
from typing import List, Dict, Any
from app.objects.c_executor import Executor

@dataclass
class Ability:
    ability_id: str
    name: str
    description: str
    tactic: str
    technique_id: str
    technique_name: str
    executors: List[Executor]
    requirements: List[Dict[str, Any]] = field(default_factory=list)
    repeatable: bool = False
    timeout: int = 60
    access: Dict[str, Any] = field(default_factory=dict)
    additional_info: Dict[str, Any] = field(default_factory=dict)
