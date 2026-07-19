from dataclasses import dataclass
import os
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    data_dir: Path
    agent_mode: str = "deterministic"


def default_data_dir() -> Path:
    return Path(__file__).resolve().parents[3] / "data"


def build_settings(data_dir: Path | None = None, agent_mode: str | None = None) -> Settings:
    env_data_dir = os.getenv("DATA_DIR")
    resolved_agent_mode = agent_mode or os.getenv("AGENT_MODE", "deterministic")
    resolved_data_dir = data_dir or (Path(env_data_dir) if env_data_dir else default_data_dir())
    return Settings(data_dir=resolved_data_dir, agent_mode=resolved_agent_mode)
