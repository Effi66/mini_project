from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    data_dir: Path
    agent_mode: str = "deterministic"


def default_data_dir() -> Path:
    return Path(__file__).resolve().parents[3] / "data"


def build_settings(data_dir: Path | None = None, agent_mode: str = "deterministic") -> Settings:
    return Settings(data_dir=data_dir or default_data_dir(), agent_mode=agent_mode)

