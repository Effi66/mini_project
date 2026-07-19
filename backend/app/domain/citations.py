from pathlib import Path

from app.models.policy import Citation


def build_citation(data_dir: Path, policy_file: Path, json_path: str, quote: str) -> Citation:
    try:
        relative_path = policy_file.relative_to(data_dir.parent).as_posix()
    except ValueError:
        relative_path = policy_file.name

    return Citation(source_file=relative_path, json_path=json_path, quote=quote)

