from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List


@dataclass(frozen=True)
class Paths:
    project_root: Path
    package_root: Path
    data_dir: Path
    output_dir: Path


def get_paths() -> Paths:
    package_root = Path(__file__).resolve().parent.parent
    project_root = package_root.parent
    data_dir = package_root / "data"
    output_dir = package_root / "outputs"
    output_dir.mkdir(exist_ok=True)
    return Paths(
        project_root=project_root,
        package_root=package_root,
        data_dir=data_dir,
        output_dir=output_dir,
    )


def load_grupos(paths: Paths | None = None) -> Dict[str, List[str]]:
    if paths is None:
        paths = get_paths()
    grupos_path = paths.data_dir / "grupos.json"
    with open(grupos_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    grupos: Dict[str, List[str]] = {}
    for row in data.get("rows", []):
        grupos[row["name"]] = [s.upper() for s in row.get("symbols", [])]
    return grupos


