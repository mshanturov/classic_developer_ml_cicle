from __future__ import annotations

from configparser import ConfigParser
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ModelConfig:
    n_estimators: int
    max_depth: int | None
    random_state: int
    test_size: float


class ConfigLoader:
    """Loads model hyperparameters from config.ini."""

    def __init__(self, config_path: str | Path) -> None:
        self.config_path = Path(config_path)

    def load(self) -> ModelConfig:
        parser = ConfigParser()
        read_files = parser.read(self.config_path)
        if not read_files:
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        max_depth_value = parser.get("model", "max_depth", fallback="none").strip().lower()
        max_depth = None if max_depth_value in {"none", "null", ""} else int(max_depth_value)

        return ModelConfig(
            n_estimators=parser.getint("model", "n_estimators", fallback=300),
            max_depth=max_depth,
            random_state=parser.getint("model", "random_state", fallback=42),
            test_size=parser.getfloat("data", "test_size", fallback=0.2),
        )
