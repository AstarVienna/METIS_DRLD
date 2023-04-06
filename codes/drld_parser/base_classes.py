import dataclasses
from typing import Dict, Set, List, Tuple


@dataclasses.dataclass
class FitsHeader:
    parameter: str
    hidden: str
    range: str
    label: str


@dataclasses.dataclass
class Template:
    name: str
    ttype: str
    headers: Dict[str, FitsHeader]
    references: Set[str]


@dataclasses.dataclass
class Recipe:
    name: str = None
    purpose: str = None
    type: str = None
    templates: List[str] = None
    input_data: List[str] = None
    parameters: List[str] = None
    algorithm: str = None
    output_data: List[Tuple[str, str]] = None
    expected_accuracies: str = None
    qc1_parameters: List[str] = None
    hdrl_functions: List[str] = None
    requirements: List[str] = None
    matched_keywords: List[str] = None

