from __future__ import annotations

import json
from pathlib import Path

from .models import RawDataset, Recommendation


def load_records(path: str | Path) -> list[RawDataset]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return [RawDataset.model_validate(record) for record in payload]


def write_recommendations(items: list[Recommendation], path: str | Path) -> None:
    output = [item.model_dump(mode="json") for item in items]
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")

