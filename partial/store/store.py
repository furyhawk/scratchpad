from typing import Any

from dataclasses import dataclass, field
from pathlib import Path

# from utils.general_utils import generate_uuid4


# @dataclass(frozen=False, init=True)
# class Stores:
#     """A class to keep track of model artifacts."""

#     logs_dir: Path = field(init=True)
#     project_name: str = "CIFAR-10"
#     unique_id: str = unique_id()#field(default_factory=generate_uuid4)


# @dataclass(frozen=False, init=True)
class Stores:
    """A class to keep track of model artifacts."""

    def __init__(self, logs_dir, project_name, unique_id: Any):
        super().__init__()
        self.logs_dir: Path = Path(logs_dir)
        self.project_name: str = project_name
        self.unique_id = unique_id()

    def __repr__(self) -> str:
        return f"Stores(unique_id={self.unique_id})"
